"""Stream-only Stremio addon endpoints (movies and series)."""
import base64, binascii, hmac, logging, re
from aiohttp import web
from yarl import URL
from config import API_PASSWORD

logger=logging.getLogger(__name__)
ADDON_ID="community.easyproxy.movies-series"
_ID_RE=re.compile(r"^(tt\d{5,12})(?::(\d{1,3}):(\d{1,4}))?$",re.I)

def _decode(token):
    try:
        token += "=" * (-len(token)%4)
        return base64.urlsafe_b64decode(token.encode("ascii")).decode("utf-8")
    except (ValueError,UnicodeError,binascii.Error):
        return ""

def _auth(request):
    return not API_PASSWORD or hmac.compare_digest(_decode(request.match_info.get("token","")),API_PASSWORD)

def _parse(kind,item):
    m=_ID_RE.fullmatch(item or "")
    if not m:return None
    imdb,s,e=m.groups()
    if kind=="movie" and s is None:return imdb,None,None
    if kind=="series" and s is not None and e is not None:
        s,e=int(s),int(e)
        if s>=0 and e>0:return imdb,s,e
    return None

def setup_stremio_routes(app,proxy):
    async def manifest(request):
        if not _auth(request):return web.json_response({"error":"Unauthorized"},status=401)
        return web.json_response({"id":ADDON_ID,"version":"1.0.0","name":"EasyProxy Movies & Series","description":"Stream resolver for Cinemeta IMDb movie and episode IDs.","resources":["stream"],"types":["movie","series"],"idPrefixes":["tt"],"behaviorHints":{"configurable":False,"configurationRequired":False}})
    async def streams(request):
        if not _auth(request):return web.json_response({"streams":[]},status=401)
        kind,item=request.match_info["type"],request.match_info["item_id"]
        parsed=_parse(kind,item)
        if not parsed:return web.json_response({"streams":[]})
        imdb,s,e=parsed
        source=f"https://vidfast.vc/movie/{imdb}" if kind=="movie" else f"https://vidfast.vc/tv/{imdb}/{s}/{e}"
        query={"host":"vidfast","d":source,"redirect_stream":"true"}
        if API_PASSWORD:query["api_password"]=API_PASSWORD
        internal=request.clone(rel_url=URL("/extractor/video").with_query(query))
        try:
            response=await proxy.handle_extractor_request(internal)
            loc=response.headers.get("Location")
            if loc and response.status in (301,302,303,307,308):
                return web.json_response({"streams":[{"url":loc,"title":"EasyProxy • VidFast","behaviorHints":{"notWebReady":True}}]})
            logger.warning("Stremio extractor status %s for %s",response.status,item)
            return web.json_response({"streams":[]})
        except web.HTTPException as exc:
            loc=exc.headers.get("Location")
            if loc:return web.json_response({"streams":[{"url":loc,"title":"EasyProxy • VidFast","behaviorHints":{"notWebReady":True}}]})
            logger.warning("Stremio HTTP exception for %s: %s",item,exc.status)
            return web.json_response({"streams":[]})
        except Exception:
            logger.exception("Stremio resolver failed for %s",item)
            return web.json_response({"streams":[]})
    if API_PASSWORD:
        app.router.add_get("/stremio/{token}/manifest.json",manifest)
        app.router.add_get("/stremio/{token}/stream/{type}/{item_id}.json",streams)
    else:
        app.router.add_get("/stremio/manifest.json",manifest)
        app.router.add_get("/stremio/stream/{type}/{item_id}.json",streams)
