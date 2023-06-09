from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from apprise import Apprise, AppriseAttachment
from selenium import webdriver
from dotenv import load_dotenv
import os
import time
import datetime
# from selenium.webdriver.firefox.options import Options # Bu hiç kullanılmadığı için comment yaptım.
import requests
import pickle


# Telegram botu için sağlayıcı bilgileri
channels = os.getenv('CHANNELS')
apobj = Apprise()
# Kanalları ekleme
for channel in channels:
    apobj.add(channel)

options = webdriver.FirefoxOptions()
options.set_preference("network.http.prompt-temp-redirect", False)
options.set_preference("network.http.prompt-temp-redirect.show-dialog", False)
options.accept_insecure_certs = True
options.add_argument('--headless')

driver = webdriver.Firefox(options=options)
yks_url = "https://forum.donanimhaber.com/yeni-konu-2642"
msu_url = "https://forum.donanimhaber.com/yeni-konu-2642"
ales_url = "https://forum.donanimhaber.com/yeni-konu-1997"
yds_url = "https://forum.donanimhaber.com/yeni-konu-1996"
tusvb_url = "https://forum.donanimhaber.com/yeni-konu-2703"
kpss_url = "https://forum.donanimhaber.com/yeni-konu-1995"


def discordsend(message="çalıştı") -> None:
    webhook_url = os.getenv('WEBHOOK_URL')
    payload = {'content': message}
    requests.post(webhook_url, json=payload)  # Discord mesajı gönder


def discorderror(ex) -> None:
    webhook_url_ex = os.getenv('WEBHOOK_URL_EX')
    payload = {'content': f"{type(ex).__name__}: {ex}"}
    requests.post(webhook_url_ex, json=payload)  # Discord mesajı gönder


def durum(message) -> None:
    now = str(datetime.datetime.now())
    print(f"{message} {now}")


def osym_giris() -> AppriseAttachment:
    global result, my_list
    url = "https://sonuc.osym.gov.tr/"
    driver.get(url)
    discordsend("ösym site girildi")
    time.sleep(3)
    driver.save_screenshot("ösym.png")
    results = driver.find_elements(By.CSS_SELECTOR, "#grdSonuclar > tbody > tr > td:nth-child(1) > a")
    my_list = []
    for i in results:
        my_list.append(i.text)
    result = '\n'.join(my_list)


def dosya_okuma() -> None:
    global content
    with open("newfile.txt", "r", encoding="utf-8") as f:
        content = f.read()
    discordsend("dosya okundu")


def konu_ac(sinav_adi, url) -> None:
    discordsend("farklılık tespit edildi")
    with open("newfile.txt", "w", encoding="utf-8") as f:
        f.write(result)
    with open("newfile.txt", "r", encoding="utf-8") as file:
        first_line = file.readline().strip()  # İlk satırı oku ve '\n' karakterini atla
    link = driver.find_element(By.CSS_SELECTOR, "#grdSonuclar > tbody > tr:nth-child(2) > td:nth-child(1) > a")
    link2 = link.get_attribute("href")
    discordsend("mevcut url alındı")

    apobj.notify(body=f'Yeni Sınav Sonucu:\n{first_line}\n{link2}', attach="ösym.png")
    driver.get(url)
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)
    discordsend("cookie yüklendi")

    driver.refresh()
    kbaslik = driver.find_element(By.CSS_SELECTOR, "#ilan-baslik-standard")
    kbaslik.click()
    kbaslik.send_keys(f"AÇIKLANDI {sinav_adi} (OTOMATİK MESAJ)")
    discordsend("Başlık girildi")

    aciklama = driver.find_element(By.CSS_SELECTOR, ".ql-editor")
    aciklama.click()
    aciklama.send_keys(f"{first_line} AÇIKLANDI", Keys.ENTER, Keys.ENTER, link2)
    discordsend("açıklama girildi")
    time.sleep(5)
    k_ac = driver.find_element(By.CSS_SELECTOR, "#editor-toolbar-container_0 > div > div > button")
    k_ac.click()
    discordsend("konu açıldı")
    time.sleep(4)
    current_url2 = driver.current_url
    apobj.notify(body=f"Konu açtım: \n {current_url2}")


def kontrol() -> None:
    if content != result and result != "":
        if "YKS" in my_list[0]:
            konu_ac("YKS", yks_url)

        elif "MSÜ" in my_list[0]:
            konu_ac("MSÜ", msu_url)

        elif "ALES" in my_list[0]:
            konu_ac("ALES", ales_url)

        elif "YDS" in my_list[0]:
            konu_ac("YDS", yds_url)

        elif "(TUS)" in my_list[0] or "(DUS)" in my_list[0] or "(YDUS)" in my_list[0] or "(EUS)" in my_list[0]:
            konu_ac("TUS/DUS/YDUS/EUS", tusvb_url)

        elif "KPSS" in my_list[0]:
            konu_ac("KPSS", kpss_url)


def main():
    while True:
        try:
            load_dotenv()
            osym_giris()
            dosya_okuma()
            kontrol()
            time.sleep(20)
        except Exception as Ex:
            discorderror(Ex)
            time.sleep(20)


if __name__ == "__main__":
    main()