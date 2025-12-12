import json
from typing import Any, Dict, Optional

import redis.asyncio as redis
from config import Redis, config, logger


class RedisManager:
    """
    Classe genérica para manipulação do Redis
    """

    def __init__(self, config: Redis):
        self.redis = redis.Redis(
            password=config.password,
            host=config.host,
            port=config.port,
            db=config.db,
            decode_responses=True,
        )

    async def insert(
        self, key: str, value: str | int | Dict[str, Any], time: int
    ):
        """
        Função genérica para inserir dados com TTL
        Args:
            key: Chave do Redis
            value: Valor a ser armazenado
            time: Tempo de vida em segundos
        """
        if isinstance(value, dict):
            value = json.dumps(value)

        await self.redis.setex(name=str(key), time=time, value=value)

    async def search(self, key: str) -> Optional[str]:
        """
        Função genérica para buscar dados
        Args:
            key: Chave do Redis
        Returns:
            Valor encontrado ou None
        """
        result = await self.redis.get(key)
        return result

    async def delete(self, key: str) -> bool:
        """
        Função genérica para deletar dados
        Args:
            key: Chave do Redis
        Returns:
            True se deletado, False se não existia
        """
        result = await self.redis.delete(key)
        return bool(result)

    async def expire(self, key: str, time: int) -> bool:
        """
        Define tempo de expiração para uma chave
        Args:
            key: Chave do Redis
            time: Tempo em segundos
        Returns:
            True se definido, False se chave não existe
        """
        result = await self.redis.expire(key, time)
        return bool(result)

    async def close(self):
        """Fecha a conexão com o Redis"""
        await self.redis.close()


class SessionManager(RedisManager):
    def __init__(self, config: Redis = config.redis):
        super().__init__(config)

        # Script Lua para criação atômica de sessão
        self.create_session_script = """
        local id = ARGV[1]
        local session_id = ARGV[2]
        local session_data = ARGV[3]
        local ttl = tonumber(ARGV[4])
        
        -- Cria nova sessão
        redis.call('SETEX', 'session:' .. session_id, ttl, session_data)
        redis.call('SETEX', 'user_session:' .. id, ttl, session_id)
        
        return session_id
        """

        self.previous_session_script = """
        local id = ARGV[1]
        local session_id = ARGV[2]
        local session_data = ARGV[3]
        local ttl = tonumber(ARGV[4])
        
        -- Remove sessão anterior se existir
        local old_session = redis.call('GET', 'user_session:' .. id)
        if old_session then
            redis.call('DEL', 'session:' .. old_session)
            redis.call('DEL', 'user_session:' .. id)
        end
        
        -- Cria nova sessão
        redis.call('SETEX', 'session:' .. session_id, ttl, session_data)
        redis.call('SETEX', 'user_session:' .. id, ttl, session_id)
        
        return session_id
        """

        # Script Lua para logout por session_id
        self.logout_session_script = """
        local session_id = ARGV[1]
        
        -- Busca dados da sessão
        local session_data = redis.call('GET', 'session:' .. session_id)
        
        if session_data then
            local data = cjson.decode(session_data)
            local id = data.user_id
            
            if id then
                -- Remove ambas as chaves
                redis.call('DEL', 'session:' .. session_id)
                redis.call('DEL', 'user_session:' .. id)
                return 1
            end
        end
        
        return 0
        """

        # Script Lua para estender sessão
        self.extend_session_script = """
        local session_id = ARGV[1]
        local ttl = tonumber(ARGV[2])
        
        -- Busca dados da sessão
        local session_data = redis.call('GET', 'session:' .. session_id)
        
        if session_data then
            local data = cjson.decode(session_data)
            local id = data.user_id
            
            if id then
                -- Estende ambas as chaves
                redis.call('EXPIRE', 'session:' .. session_id, ttl)
                redis.call('EXPIRE', 'user_session:' .. id, ttl)
                return 1
            end
        end
        
        return 0
        """

    async def create(
        self,
        session_id: str,
        data: Dict[str, Any],
        ttl: int = config.redis.ttl,
    ) -> str:
        """
        Cria uma nova sessão para o usuário de forma atômica usando Lua
        Args:
            session_id: ID da sessão
            data: Dados do usuário para armazenar na sessão
            ttl: Tempo de vida da sessão em segundos (padrão: 1 hora)
        Returns:
            session_id: Uid v7 gerado para a sessão
        """

        # Executa script Lua atômico
        response = await self.redis.eval(
            self.create_session_script,
            0,  # sem chaves
            data['id'],
            session_id,
            json.dumps(data),
            str(ttl),
        )
        logger.info(f'Session created: {session_id} {response}')
        return session_id

    async def get_session_data(
        self, session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Recupera os dados da sessão pelo session_id
        Args:
            session_id: ID da sessão
        Returns:
            Dados do usuário ou None se não encontrado
        """
        data = await self.search(f'session:{session_id}')
        if data:
            return json.loads(data)
        return None

    async def get_user_session_id(self, user_id: str) -> Optional[str]:
        """
        Recupera o session_id ativo do usuário
        Args:
            user_id: ID do usuário
        Returns:
            session_id ativo ou None se não encontrado
        """
        return await self.search(f'user_session:{user_id}')

    async def validate_session(
        self, session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Valida se a sessão existe e retorna os dados do usuário
        Args:
            session_id: ID da sessão
        Returns:
            Dados do usuário ou None se sessão inválida
        """
        return await self.get_session_data(session_id)

    async def logout_user(self, user_id: str) -> bool:
        """
        Remove a sessão ativa do usuário de forma atômica usando Lua
        Args:
            user_id: ID do usuário
        Returns:
            True se a sessão foi removida, False se não existia
        """
        result = await self.redis.eval(
            self.logout_script,
            0,  # sem chaves
            user_id,
        )
        return bool(result)

    async def logout_session(self, session_id: str) -> bool:
        """
        Remove uma sessão específica de forma atômica usando Lua
        Args:
            session_id: ID da sessão
        Returns:
            True se a sessão foi removida, False se não existia
        """
        result = await self.redis.eval(
            self.logout_session_script,
            0,  # sem chaves
            session_id,
        )
        return bool(result)

    async def extend_session(
        self, session_id: str, ttl_seconds: int = 3600
    ) -> bool:
        """
        Estende o tempo de vida de uma sessão de forma atômica usando Lua
        Args:
            session_id: ID da sessão
            ttl_seconds: Novo tempo de vida em segundos
        Returns:
            True se a sessão foi estendida, False se não existe
        """
        result = await self.redis.eval(
            self.extend_session_script,
            0,  # sem chaves
            session_id,
            str(ttl_seconds),
        )
        return bool(result)

    async def previous_session(
        self,
        session_id: str,
        data: Dict[str, Any],
        ttl: int = config.redis.ttl,
    ) -> bool:
        """
        Invalida sessão anterior do usuário se modo UNIQUE e cria nova sessão
        Args:
            session_id: ID da nova sessão
            data: Dados do usuário para a nova sessão
            ttl: Tempo de vida da sessão
        Returns:
            True se sessão anterior foi invalidada, False se não havia sessão anterior
        """
        response = await self.redis.eval(
            self.previous_session_script,
            0,  # sem chaves
            data['id'],
            session_id,
            json.dumps(data),
            str(ttl),
        )
        logger.info(f'Session created: {session_id} {response}')
        return response


# Instância global do gerenciador Redis
redis_manager = RedisManager(config=config.redis)
session_manager = SessionManager()
