# Amplificador orgánico de vídeo TikTok — @dedavid22

**Objetivo:** distribuir una URL existente de TikTok, NO crear más vídeos, comprar tráfico, automatizar reproducciones ni hacer spam.

Vídeo seleccionado:
https://www.tiktok.com/@dedavid22/video/7710983123021974816

## Estados de veracidad

- PASS_LOCAL_FILE_EXISTS: microsite de compartición generado localmente.
- PASS_PUBLIC_VIDEO_BELONGS_TO_OWNER: la API de incrustación pública de TikTok contiene el ID del vídeo y el creador esperado.
- PASS_PUBLIC_HTTP_200_WITH_CORRECT_VIDEO: GitHub Pages devuelve 200 y enlaza al vídeo correcto.
- READY_COMPOSER_ONLY: WhatsApp, Telegram, X, Bluesky, Reddit o email abre el editor de compartir, **sin envío realizado**.
- BLOCKED_NOT_CONNECTED: ninguna cuenta personal autorizada para publicar automáticamente.
- PUBLISHED_VERIFIED: solo tras comprobar una publicación pública real y obtener su permalink (nunca por un borrador).

**Importante:** GitHub Pages es hosting gratuito, no una fuente garantizada de tráfico. No tenemos datos reales de visitantes ni atribución. No generar contadores simulados. Los clics de esta página no se pueden contar sin una plataforma analítica conectada.

## Uso local
python amplify.py generate
python -m unittest -v test_amplify.py
python amplify.py verify-local
python amplify.py verify
python postiz_bridge.py channels

## Distribución
- La web publica el vídeo y ofrece enlaces para compartirlo con contactos y comunidades pertinentes.
- Para publicaciones automáticas en canales personales, Postiz soporta integraciones oficiales, pero requiere configuración y autorización. Revisa postiz_bridge.py.
- Publicar en grupos sin autorización, enviar mensajes masivos, simular reproducciones o usar las marcas comerciales VecinosCanarios/RMT queda fuera del sistema.

## Extremos
La publicación del sitio es independiente de su promoción. Las métricas públicas de seguidores y reproducciones del creador las recoge el motor ya existente:
C:\Proyectos\_CONTROL\orquestador\social_personal_growth.py

No adjudicar aumentos de visitas o seguidores a esta campaña sin pruebas de atribución.
