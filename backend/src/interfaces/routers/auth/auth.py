from fastapi import APIRouter, Depends, Request, Response

from src.infra.security.auth import get_current_user

router = APIRouter(prefix='/otp')


def _ensure_png_bytes(image_any) -> bytes:
    if isinstance(image_any, bytes):
        return image_any
    if isinstance(image_any, str):
        # assume base64 sem prefixo data:; se tiver, remova o cabeçalho antes
        return base64.b64decode(image_any)
    try:
        # Tentativa: objeto PIL.Image
        from PIL import Image

        if isinstance(image_any, Image.Image):
            buf = io.BytesIO()
            image_any.save(buf, format='PNG')
            return buf.getvalue()
    except Exception:
        pass
    raise TypeError('Formato de imagem não suportado')


@router.get('/create')
async def create(
    request: Request,
    response: Response,
    data=Depends(get_current_user),
):
    pass


@router.get('/create/qrcode')
async def create_qrcode(
    request: Request,
    response: Response,
    data=Depends(get_current_user),
):
    pass


""" @router.post('/verify')
async def verify(
    request: Request,
    response: Response,
    opt_code: Query(str, pattern=r'^\d{6}$'),
):
    pass
 """
