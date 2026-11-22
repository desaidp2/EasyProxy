# EasyProxy Stremio Movies & Series

Stream-only Stremio addon integration registered in EasyProxy.

- Cinemeta is expected to provide catalogs and metadata.
- This addon resolves IMDb IDs through EasyProxy's VidFast extractor.
- Movies: `tt1234567`
- Episodes: `tt1234567:1:2` (IMDb ID, season, episode)
- Live TV is intentionally not included.

## Install

Run EasyProxy, then install this addon URL in Stremio:

`http://YOUR-EASYPROXY-HOST:7860/stremio/<base64url-api-password>/manifest.json`

The token is URL-safe Base64 of the API password without padding (default password is `ep`; token `ZXA`). This is encoding, not encryption. Use HTTPS and a strong custom API password for public servers.

Default-password example only:

`http://YOUR-EASYPROXY-HOST:7860/stremio/ZXA/manifest.json`

The extractor is called internally with the VidFast host selector; playback is returned via EasyProxy's proxy redirect.
