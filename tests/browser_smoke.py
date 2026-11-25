"""Deterministic browser acceptance check; run in GitHub CI."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json, shutil, tempfile, threading
from urllib.parse import urlparse,parse_qs
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

def main():
    screenshots=ROOT/'browser-checks';screenshots.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copytree(ROOT/'dist',Path(tmp)/'wikitrails')
        server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=tmp));threading.Thread(target=server.serve_forever,daemon=True).start()
        try:
            with sync_playwright() as p:
                browser=p.chromium.launch();page=browser.new_page(viewport={'width':1280,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                payload={'query':{'pages':{'1':{'pageid':1,'title':'Harbour landmark','extract':'A historic waterfront place.','lastrevid':77,'coordinates':[{'lat':44.648,'lon':-63.572}]},'2':{'pageid':2,'title':'Railway station','extract':'A former railway terminus.','lastrevid':78,'coordinates':[{'lat':44.650,'lon':-63.570}]}}}}
                held=[]
                def source(route):
                    coord=parse_qs(urlparse(route.request.url).query).get('ggscoord',[''])[0]
                    if coord.startswith('44.3778|'):held.append(route)
                    else:route.fulfill(status=200,content_type='application/json',body=json.dumps(payload),headers={'access-control-allow-origin':'*'})
                page.route('https://en.wikipedia.org/w/api.php?*',source)
                page.route('https://tile.openstreetmap.org/**',lambda r:r.abort())
                page.goto(f'http://127.0.0.1:{server.server_port}/wikitrails/')
                page.locator('.card').first.wait_for();assert page.locator('.card').count()==2
                pictures=page.get_by_role('link',name='Pictures of this place').first.get_attribute('href');assert pictures=='https://coolcode.ca/commonslens/?lat=44.648&lon=-63.572'
                page.locator('.card button',has_text='Save place').first.click();assert page.locator('#saved-list li').count()==1
                page.reload();page.locator('.card').first.wait_for();assert page.locator('#saved-list li').count()==1
                assert page.locator('#presets button').count()==3
                assert page.locator('#preset optgroup').count()>=6
                page.locator('#preset').select_option(label='Lunenburg');page.get_by_text('Loading nearby articles…',exact=True).wait_for();assert page.locator('.card').count()==0
                page.wait_for_timeout(150);assert held
                held[0].fulfill(status=200,content_type='application/json',body=json.dumps(payload),headers={'access-control-allow-origin':'*'});page.locator('.card').first.wait_for()
                page.locator('#preset').select_option(label='Victoria');page.locator('.card').first.wait_for();assert 'Victoria' in page.locator('#results-heading').inner_text()
                page.locator('#filter').fill('railway');assert page.locator('.card').count()==1
                page.locator('#place').fill('Dartmouth');page.get_by_role('button',name='Find place',exact=True).click();page.locator('#place-options button').first.wait_for();page.locator('#place-options button').first.click()
                page.locator('#filter').fill('');page.screenshot(path=str(screenshots/'desktop.png'),full_page=True)
                page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(screenshots/'mobile.png'),full_page=True)
                assert not errors,errors;browser.close()
        finally:server.shutdown()
    print('Wiki Trails browser checks passed')
if __name__=='__main__':main()
