"""Deterministic browser acceptance check; run in GitHub CI."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json, shutil, tempfile, threading
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
                page.route('https://en.wikipedia.org/w/api.php?*',lambda r:r.fulfill(status=200,content_type='application/json',body=json.dumps(payload),headers={'access-control-allow-origin':'*'}))
                page.route('https://tile.openstreetmap.org/**',lambda r:r.abort())
                page.goto(f'http://127.0.0.1:{server.server_port}/wikitrails/')
                page.locator('.card').first.wait_for();assert page.locator('.card').count()==2
                page.locator('.card button',has_text='Save place').first.click();assert page.locator('#saved-list li').count()==1
                page.reload();page.locator('.card').first.wait_for();assert page.locator('#saved-list li').count()==1
                page.locator('#filter').fill('railway');assert page.locator('.card').count()==1
                page.locator('#place').fill('Dartmouth');page.get_by_role('button',name='Find place',exact=True).click();page.locator('#place-options button').first.wait_for();page.locator('#place-options button').first.click()
                page.locator('#filter').fill('');page.screenshot(path=str(screenshots/'desktop.png'),full_page=True)
                page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(screenshots/'mobile.png'),full_page=True)
                assert not errors,errors;browser.close()
        finally:server.shutdown()
    print('Wiki Trails browser checks passed')
if __name__=='__main__':main()
