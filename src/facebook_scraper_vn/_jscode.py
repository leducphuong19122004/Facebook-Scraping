
def getImageElement(index_container) -> str:
    js_code = f"var nodes = [];let currentNode = null;var result = document.evaluate(\"//div[@data-mcomponent='MContainer' and @data-type='vscroller']/div[{index_container}]//div[@data-mcomponent='ImageArea']/img[@class='img contain' and @data-type='image']\", document, null, XPathResult.ANY_TYPE, null);while ((currentNode = result.iterateNext()))nodes.push(currentNode);Array.from(nodes);"
    return js_code

def getAttributeElement(index_container, attr, name) -> str:
    if name == 'image':
        js_code = f"var nodes = [];let currentNode = null;var result = document.evaluate(\"//div[@data-mcomponent='MContainer' and @data-type='vscroller']/div[{index_container}]//div[@data-mcomponent='ImageArea']/img[@class='img contain' and @data-type='image']\", document, null, XPathResult.ANY_TYPE, null);while ((currentNode = result.iterateNext()))nodes.push(currentNode);Array.from(nodes, node=>node.getAttribute('{attr}'));"
        return js_code
    if name == 'video':
        js_code = f"var nodes = [];let currentNode = null;var result = document.evaluate(\"//div[@data-mcomponent='MContainer' and @data-type='vscroller']/div[{index_container}]//div[@data-mcomponent='MVideo' and @data-type='video']\", document, null, XPathResult.ANY_TYPE, null);while ((currentNode = result.iterateNext()))nodes.push(currentNode);Array.from(nodes, node=>node.getAttribute('{attr}'));"
        return js_code
    if name == 'date':
        js_code = f"document.evaluate(\"//div[@data-mcomponent='MContainer' and @data-type='vscroller']/div[{index_container}]//span[@class='f5']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.innerText"
        return js_code

def getVideoElement(index_container) -> str:
    js_code = f"var nodes = [];let currentNode = null;var result = document.evaluate(\"//div[@data-mcomponent='MContainer' and @data-type='vscroller']/div[{index_container}]//div[@data-mcomponent='MVideo' and @data-type='video']\", document, null, XPathResult.ANY_TYPE, null);while ((currentNode = result.iterateNext()))nodes.push(currentNode);Array.from(nodes);"
    return js_code

def getDateElement(index_container) -> str:
    js_code = f"document.evaluate(\"//div[@data-mcomponent='MContainer' and @data-type='vscroller']/div[{index_container}]//span[@class='f5' and @style='color:#8a8d91;']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue"
    return js_code

def getContentElement(index_container) -> str:
    js_code = f"document.evaluate(\"//div[@data-mcomponent='MContainer' and @data-type='vscroller']/div[{index_container}]/div[@class='m']/div[@class='m']/div[@data-mcomponent='TextArea' and @data-type='text']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue"
    return js_code
    