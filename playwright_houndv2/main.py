import jwt
import requests

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def main():
    START_URL = "https://oficinajudicialvirtual.pjud.cl/indexN.php"
    SEARCH_URL = "https://oficinajudicialvirtual.pjud.cl/ADIR_871/apelaciones/modal/causaApelaciones.php"

    # --- TODO - LOAD DATABASE FROM GDRIVE ---
    # --- PLAYWRIGHT ---
    with sync_playwright() as pw:
        # --- Browser init ---
        browser = pw.firefox.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = browser.new_page()

        # --- Login Page ---
        page.goto(START_URL)
        page.locator(
            "#focus button[onclick='accesoConsultaCausas();']",
            has_text="Consulta causas",
        ).click()

        # --- Fill Case Search Form ---
        page.select_option("select#competencia", label="Corte Apelaciones")  # Competencia
        page.select_option("select#conCorte", label="C.A. de La Serena")  # Corte

        page.fill("input#conRolCausa", "3298")  # ROL - TODO remove hardcode
        page.fill("input#conEraCausa", "2022")  # AÑO - TODO remove hardcode

        page.locator("select#conTipoCausa").click(force=True)
        page.select_option("select#conTipoCausa", label="Protección")  # Tipo

        page.locator("button#btnConConsulta").click()

        # page.locator("a[href='#modalDetalleApelaciones']").click()

        # --- Get Case Unique ID (3 piece JWT encoded data) ---
        raw_case = page.locator("a[href='#modalDetalleApelaciones']").get_attribute("onclick")
        case_jwt_encoded = raw_case.split("'")[1]

        # --- TODO - Decode JWT encoded body ---
        # PREFIX, body, SUFFIX = case_jwt_encoded.split(".")
        # print(f"Prefix: {PREFIX}")
        # print(f"Body: {body}")
        # print(f"Suffix: {SUFFIX}")

        jwt_options = {
            "verify_signature": False
        }

        case_jwt_decoded = jwt.decode(
            case_jwt_encoded,
            algorithms=["HS256"],
            options=jwt_options
        )
        print(case_jwt_decoded)
        print(type(case_jwt_decoded))
        rol = case_jwt_decoded["data"]["rolCausa"]
        era = case_jwt_decoded["data"]["eraCausa"]
        print(rol)
        exit()



        # --- Get Case Details ---
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
            "Host": "oficinajudicialvirtual.pjud.cl",
            "Accept": "text/html, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            # "Content-Length": "926",
            "Origin": "https://oficinajudicialvirtual.pjud.cl",
            "Connection": "keep-alive",
            "Referer": "https://oficinajudicialvirtual.pjud.cl/indexN.php",
            # "Cookie": "PHPSESSID=a3be543fe833dcc822e280eac807ff26; TS01262d1d=01b485afe585660d4c67014dbae081e834d7645796134f6239f97c548a3073e914ee141716aed35ac89f551655597512bdb5ed472ea4890221933232314529c1b5d4c1d0ba",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
        payload = f"dtaCausa={case_jwt_encoded}"

        response = requests.post(SEARCH_URL, headers=headers, data=payload)
        html = response.text

        soup = BeautifulSoup(html, "html.parser")
        print(soup.prettify())

        # --- Proof of Work ---
        # page.wait_for_timeout(3000)
        # page.screenshot(path="proof.png")

        browser.close()


if __name__ == "__main__":
    main()
