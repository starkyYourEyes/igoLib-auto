import urllib.request
import urllib.parse
import http.cookiejar


def get_code(url):
    query = urllib.parse.urlparse(url).query
    codes = urllib.parse.parse_qs(query).get('code')
    if codes:
        return codes.pop()
    else:
        raise ValueError("Code not found in URL")


def get_cookie_string(code):
    cookiejar = http.cookiejar.MozillaCookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookiejar))
    response = opener.open(
        "http://wechat.v2.traceint.com/index.php/urlNew/auth.html?" + urllib.parse.urlencode({
            "r": "http://wechat.v2.traceint.com/index.php/graphql/web/index.html",
            "code": code,
            "state": 1
        })
    )
    print(response)
    cookie_items = []
    for cookie in cookiejar:
        cookie_items.append(f"{cookie.name}={cookie.value}")
    cookie_string = '; '.join(cookie_items)
    return cookie_string


def main():
    url = input("Please enter the URL: ")
    # url = 'http://wechat.v2.traceint.com/index.php/graphql/?operationName=index&query=query%7BuserAuth%7BtongJi%7Brank%7D%7D%7D&code=011Kkf1w3ryUo13m3L3w3JVWZD3Kkf19&state=1'
    code = get_code(url)
    print(code)
    cookie_string = get_cookie_string(code)
    print("Cookie string: \n")
    print(cookie_string)


if __name__ == '__main__':
    main()
