from flask import render_template, request, redirect, url_for, flash
from altan.extensions import db, login_required
from altan.models import Isletme, Proje, Odeme, Sektor, Destek, Program, Notlar, Notlar2
from altan.main import main
from datetime import datetime, date


@main.route('/deneme')
def deneme_rota():
    return render_template("deneme.html")


@main.route('/')
@login_required
def index():
    odemes = db.session.query(Isletme.unvan, Isletme.vergi, Odeme.id, Odeme.karekod, Odeme.tarih, Odeme.durum) \
        .select_from(Odeme) \
        .join(Proje) \
        .join(Isletme) \
        .filter(Odeme.durum.like("BEKLEMEDE")).all()
    nots1 = Notlar.query.filter(Notlar.durum == 0).all()
    nots2 = Notlar2.query.filter(Notlar2.durum == 0).all()
    return render_template("index.html", kisiselnotlar=nots1, isselnotlar=nots2, odemeler=odemes)


# *************************************** KOSGEB ROUTINGS BEGIN ***************************************************** #

# ******* KOSGEB / İşletmeler ROUTINGS BEGIN *********#

@main.route('/isletmeler')
@login_required
def isletme():
    sektor = Sektor.query.all()
    return render_template("isletme.html", isletme=None, sektorler=sektor)


@main.route('/isletmeler', methods=["POST", "GET"])
def isletme_verisi_al():
    unvan = request.form.get("unvan_ara")
    vergi = request.form.get("vergi_no_ara")
    isletme_id_form = request.form.get("isletme_id_ara")
    if unvan:
        isletmee = Isletme.query.filter(
            Isletme.unvan.like(unvan + "%")).first()
    elif vergi:
        isletmee = Isletme.query.filter(
            Isletme.vergi.like(vergi + "%")).first()
    elif isletme_id_form:
        isletmee = Isletme.query.filter(Isletme.id == isletme_id_form).first()
    else:
        flash('Lütfen Arama Kriteri Giriniz', 'danger')
        return redirect(url_for("main.isletme"))
    if isletmee:
        isletme_id = isletmee.id
        return redirect(url_for("main.isletme_verisi_getir", isletme_id=isletme_id))
    else:
        flash('Aradığınız İşletme Veritabanında Bulunmamaktadır', 'danger')
        return redirect(url_for("main.isletme"))


@main.route('/isletmeler/<int:isletme_id>')
@login_required
def isletme_verisi_getir(isletme_id):
    isletmee = Isletme.query.filter(Isletme.id == isletme_id).first()
    programlar = Program.query.all()
    destekler = Destek.query.all()
    sektor = Sektor.query.all()
    return render_template("isletme.html", isletme=isletmee, programlar=programlar, destekler=destekler,
                           sektorler=sektor, today=date.today())


@main.route('/isletmeler/isletme-ekle/', methods=["POST", "GET"])
def isletme_verisi_ekle():
    isletme_isimleri = ["unvan", "vergi_no", "isletme_id", "sektor", "yetkili",
                        "isletme_tur", "is_mail", "tel-1", "bilgi", "adres",
                        "tel-2", "durum", "son_kobi_beyan", "bey_sat", "bey_cal"]
    if request.method == 'POST':
        isletme_bilgileri = {isim: request.form.get(isim) for isim in isletme_isimleri}
        for bilgi in isletme_bilgileri:
            if not isletme_bilgileri[bilgi]:
                isletme_bilgileri[bilgi] = 0
        isletmee = Isletme.query.filter(Isletme.id == isletme_bilgileri["isletme_id"]).first()
        if isletmee:
            isletmee.id = isletme_bilgileri["isletme_id"]
            isletmee.vergi = isletme_bilgileri["vergi_no"]
            isletmee.unvan = isletme_bilgileri["unvan"]
            isletmee.sektor_ismi = isletme_bilgileri["sektor"]
            isletmee.tur = isletme_bilgileri["isletme_tur"]
            isletmee.tel1 = isletme_bilgileri["tel-1"]
            isletmee.tel2 = isletme_bilgileri["tel-2"]
            isletmee.mail = isletme_bilgileri["is_mail"]
            isletmee.yetkili = isletme_bilgileri["yetkili"]
            isletmee.adres = isletme_bilgileri["adres"]
            isletmee.bilgi = isletme_bilgileri["bilgi"]
            isletmee.bey_yil = isletme_bilgileri["son_kobi_beyan"]
            isletmee.bey_cal = isletme_bilgileri["bey_cal"]
            isletmee.bey_sat = isletme_bilgileri["bey_sat"]
            isletmee.durum = isletme_bilgileri["durum"]
            db.session.commit()
            flash('İşletme Verileriniz güncellenmiştir', 'primary')
            return redirect(url_for("main.isletme_verisi_getir", isletme_id=isletme_bilgileri["isletme_id"]))
        else:
            if isletme_bilgileri["isletme_id"]:
                new_isletme = Isletme(id=isletme_bilgileri["isletme_id"], vergi=isletme_bilgileri["vergi_no"],
                                      unvan=isletme_bilgileri["unvan"], sektor_ismi=isletme_bilgileri["sektor"],
                                      tur=isletme_bilgileri["isletme_tur"], tel1=isletme_bilgileri["tel-1"],
                                      tel2=isletme_bilgileri["tel-2"], mail=isletme_bilgileri["is_mail"],
                                      yetkili=isletme_bilgileri["yetkili"],
                                      adres=isletme_bilgileri["adres"], bilgi=isletme_bilgileri["bilgi"],
                                      bey_yil=isletme_bilgileri["son_kobi_beyan"], bey_cal=isletme_bilgileri["bey_cal"],
                                      bey_sat=isletme_bilgileri["bey_sat"], durum=isletme_bilgileri["durum"])
                db.session.add(new_isletme)
                db.session.commit()
                flash('İşletme Veritabanına Eklenmiştir', 'success')
                return redirect(url_for("main.isletme_verisi_getir", isletme_id=isletme_bilgileri["isletme_id"]))
            else:
                flash('Lütfen İşletme Ana Bilgilerini Giriniz', 'danger')
                return redirect(url_for("main.isletme"))
    else:
        flash('Veriler Alınamamıştır', 'danger')
        return redirect(url_for("main.isletme"))


@main.route('/isletmeler/proje-ekle/<int:isletme_id>/', methods=["POST", "GET"])
def proje_verisi_ekle(isletme_id):
    proje_isimleri = ["proje-isletme-ekle", "proje_program_ekle", "baslama-tarihi-ekle",
                      "proje-sure", "tamamlanma-tarihi-ekle", "takip-tarihi-ekle", "proje-durum", "izleyici-ekle"]
    if request.method == 'POST':
        proje_bilgileri = {isim: request.form.get(
            isim) for isim in proje_isimleri}
        takip = request.form.get("varyok2")
        if takip == "yok":
            proje_bilgileri["takip-tarihi-ekle"] = "2087-09-09"    
        new_proje = Proje(isletme_id=proje_bilgileri["proje-isletme-ekle"],
                          program_ismi=proje_bilgileri["proje_program_ekle"],
                          baslama_tarihi=datetime.strptime(
                              proje_bilgileri["baslama-tarihi-ekle"], '%Y-%m-%d'),
                          tamamlanma_tarihi=datetime.strptime(
                              proje_bilgileri["tamamlanma-tarihi-ekle"], '%Y-%m-%d'),
                          takip_tarihi=datetime.strptime(
                              proje_bilgileri["takip-tarihi-ekle"], '%Y-%m-%d'),
                          sure=proje_bilgileri["proje-sure"], durum=proje_bilgileri["proje-durum"],
                          izleyici=proje_bilgileri["izleyici-ekle"], koordinator="", notlar="", izleme="")
        db.session.add(new_proje)
        db.session.commit()
        flash('Ödeme Veritabanına Eklenmiştir', 'success')
        return redirect(url_for("main.isletme_verisi_getir", isletme_id=isletme_id))
    else:
        flash('Veriler Alınamamıştır', 'danger')
        return redirect(url_for("main.isletme"))


@main.route('/isletmeler/proje-guncelle/<int:isletme_id>/<int:proje_id>/', methods=["POST", "GET"])
def isletme_proje_verisi_guncelle(isletme_id, proje_id):
    isimler = ["projeler-baslamatarihi-guncelle", "projeler-sure-guncelle", "projeler-tamamlanmatarihi-guncelle",
               "projeler-takiptarihi-guncelle", "projeler-durum-guncelle", "projeler-izleyici-guncelle",
               "projeler-koordinator-guncelle", "projeler-notlar-guncelle", "projeler-izleme-guncelle"]
    if request.method == 'POST':
        proje_bilgileri = {isim: request.form.get(isim) for isim in isimler}
        takip = request.form.get("varyok3")
        proje = Proje.query.filter(Proje.id == proje_id).first()
        proje.baslama_tarihi = datetime.strptime(
            proje_bilgileri["projeler-baslamatarihi-guncelle"], '%Y-%m-%d')
        proje.sure = proje_bilgileri["projeler-sure-guncelle"]
        proje.tamamlanma_tarihi = datetime.strptime(
            proje_bilgileri["projeler-tamamlanmatarihi-guncelle"], '%Y-%m-%d')
        if takip == "yok":
            proje_bilgileri["projeler-takiptarihi-guncelle"] = "2087-09-09" 
        proje.takip_tarihi = datetime.strptime(
            proje_bilgileri["projeler-takiptarihi-guncelle"], '%Y-%m-%d')
        proje.durum = proje_bilgileri["projeler-durum-guncelle"]
        proje.izleyici = proje_bilgileri["projeler-izleyici-guncelle"]
        proje.koordinator = proje_bilgileri["projeler-koordinator-guncelle"]
        proje.notlar = proje_bilgileri["projeler-notlar-guncelle"]
        proje.izleme = proje_bilgileri["projeler-izleme-guncelle"]
        db.session.commit()
        flash('Proje Verileri Güncellenmiştir.', 'success')
        return redirect(url_for("main.isletme_verisi_getir", isletme_id=isletme_id))
    else:
        flash('Veriler Alınamamıştır', 'danger')
        return redirect(url_for("main.isletme"))


@main.route('/isletmeler/proje-sil/<int:isletme_id>/<int:proje_id>/')
def isletme_proje_verisi_sil(isletme_id, proje_id):
    proje = Proje.query.filter(Proje.id == proje_id).first()
    if not proje.odemeler:
        db.session.delete(proje)
        db.session.commit()
        flash('Seçilen Proje Silinmiştir', 'success')
        return redirect(url_for("main.isletme_verisi_getir", isletme_id=isletme_id))
    else:
        flash('Seçilen Projeye Bağlı Ödemeler Olduğu İçin Proje Silinememiştir.', 'danger')
        return redirect(url_for("main.isletme_verisi_getir", isletme_id=isletme_id))


@main.route('/isletmeler/odeme-ekle/<int:isletme_id>/', methods=["POST", "GET"])
def odeme_verisi_ekle(isletme_id):
    odeme_isimleri = ["proje_ekle", "destek_ekle", "kadekod-ekle",
                      "odeme-tarih-ekle", "tutar-ekle", "durum_ekle"]
    if request.method == 'POST':
        odeme_bilgileri = {isim: request.form.get(
            isim) for isim in odeme_isimleri}
        new_odeme = Odeme(karekod=odeme_bilgileri["kadekod-ekle"], tutar=odeme_bilgileri["tutar-ekle"],
                          tarih=datetime.strptime(
                              odeme_bilgileri["odeme-tarih-ekle"], '%Y-%m-%d'),
                          durum=odeme_bilgileri["durum_ekle"], proje_id=odeme_bilgileri["proje_ekle"],
                          destek_ismi=odeme_bilgileri["destek_ekle"])
        db.session.add(new_odeme)
        db.session.commit()
        flash('Ödeme Veritabanına Eklenmiştir', 'success')
        return redirect(url_for("main.isletme_verisi_getir", isletme_id=isletme_id))
    else:
        flash('Veriler Alınamamıştır', 'danger')
        return redirect(url_for("main.isletme"))


@main.route('/isletmeler/odeme-guncelle/<int:isletme_id>/<int:odeme_id>/', methods=["POST", "GET"])
def isletme_odeme_verisi_guncelle(isletme_id, odeme_id):
    isimler = ["odeme-destek-guncelle", "odeme-kadekod-guncelle", "odeme-tarih-guncelle", "odeme-tutar-guncelle",
               "odeme-durum-guncelle"]
    if request.method == 'POST':
        odeme_bilgileri = {isim: request.form.get(isim) for isim in isimler}
        odeme = Odeme.query.filter(Odeme.id == odeme_id).first()
        odeme.karekod = odeme_bilgileri["odeme-kadekod-guncelle"]
        odeme.destek_ismi = odeme_bilgileri["odeme-destek-guncelle"]
        odeme.tarih = datetime.strptime(
            odeme_bilgileri["odeme-tarih-guncelle"], '%Y-%m-%d')
        odeme.tutar = odeme_bilgileri["odeme-tutar-guncelle"]
        odeme.durum = odeme_bilgileri["odeme-durum-guncelle"]
        db.session.commit()
        flash('Ödeme Verileriniz güncellenmiştir', 'primary')
        return redirect(url_for("main.isletme_verisi_getir", isletme_id=isletme_id))
    else:
        flash('Veriler Alınamamıştır', 'danger')
        return redirect(url_for("main.bekleyen_odemeler"))


@main.route('/isletmeler/odeme-sil/<int:isletme_id>/<int:odeme_id>/')
def isletme_odeme_verisi_sil(isletme_id, odeme_id):
    odeme = Odeme.query.filter(Odeme.id == odeme_id).first()
    db.session.delete(odeme)
    db.session.commit()
    flash('Seçilen Ödeme Silinmiştir', 'success')
    return redirect(url_for("main.isletme_verisi_getir", isletme_id=isletme_id))


@main.route('/isletmeler/<int:isletme_id>/mail-gonder', methods=["POST", "GET"])
def isletmeye_mail_gonder(isletme_id):
    isimler = ["isletme-mail-adresi",
               "isletme-mail-konu", "isletme-mail-icerik"]
    if request.method == 'POST':
        mail_bilgileri = {isim: request.form.get(isim) for isim in isimler}
        import win32com.client as win32
        import pythoncom
        pythoncom.CoInitialize()
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        mail.To = mail_bilgileri["isletme-mail-adresi"]
        mail.Subject = mail_bilgileri["isletme-mail-konu"]
        signature = "<br><br><br>Saygılarımla ...<br><br>Mehmet Altan<br>Kobi Uzmanı"
        mail.HtmlBody = mail_bilgileri["isletme-mail-icerik"] + signature
        mail.Display(True)
        flash('Mail Gönderilmiştir', 'success')
        return redirect(url_for("main.isletme_verisi_getir", isletme_id=isletme_id))
    else:
        flash('Veriler Alınamamıştır', 'danger')
        return redirect(url_for("main.isletme_verisi_getir", isletme_id=isletme_id))


# ******* KOSGEB / İşletmeler ROUTINGS End *********#

# ******* KOSGEB / Projeler ROUTINGS BEGIN *********#

@main.route('/projeler/', defaults={'program': "Tüm Projeler", 'durum': "Devam Ediyor"})
@main.route('/projeler/<program>/<durum>/')
@login_required
def projeleri_getir(program, durum):
    defaults = dict(program=program, durum=durum, today=date.today(), programlar=Program.query.all(),
                    program_durumlari=["Başarıyla Tamamlandı", "Başarısız Tamamlandı", "Durduruldu", "Bilgi Yok",
                                       "Devam Ediyor"])
    qprogram = program + "%" if not program == "Tüm Projeler" else "%"
    projes = db.session.query(Isletme.unvan, Isletme.vergi, Proje.program_ismi, Proje.id, Proje.baslama_tarihi,
                              Proje.sure, Proje.tamamlanma_tarihi, Proje.durum, Proje.takip_tarihi) \
        .select_from(Proje) \
        .join(Isletme) \
        .filter(Proje.durum.like(durum)) \
        .filter(Proje.program_ismi.like(qprogram)) \
        .order_by(Proje.takip_tarihi.asc()).all()
    return render_template("projeler.html", projeler=projes, defaults=defaults)


@main.route('/projeler/sorgu', methods=['POST', 'GET'])
def projeler_sorgula():
    if request.method == 'POST':
        program = request.form.get("projeler-program")
        durum = request.form.get("projeler-durum")
        return redirect(url_for("main.projeleri_getir", program=program, durum=durum))
    else:
        flash('Veriler Alınamamıştır', 'danger')
        return redirect(url_for("main.projeleri_getir"))


@main.route('/projeler/<program>/<durum>/sil/<int:proje_id>/')
def proje_sil(program, durum, proje_id):
    proje = Proje.query.filter(Proje.id == proje_id).first()
    if not proje.odemeler:
        db.session.delete(proje)
        db.session.commit()
        flash('Seçilen Proje Silinmiştir', 'success')
        return redirect(url_for("main.projeleri_getir", program=program, durum=durum))
    else:
        flash('Seçilen Projeye Bağlı Ödemeler Olduğu İçin Proje Silinememiştir.', 'danger')
        return redirect(url_for("main.projeleri_getir", program=program, durum=durum))


@main.route('/projeler/<program>/<durum>/guncelle/<int:proje_id>/', methods=['POST', 'GET'])
def proje_verisi_guncelle(program, durum, proje_id):
    isimler = ["projeler-baslamatarihi-guncelle", "projeler-sure-guncelle", "projeler-tamamlanmatarihi-guncelle",
               "projeler-takiptarihi-guncelle", "projeler-durum-guncelle"]
    if request.method == 'POST':
        proje_bilgileri = {isim: request.form.get(isim) for isim in isimler}
        takip = request.form.get("varyok")
        proje = Proje.query.filter(Proje.id == proje_id).first()
        proje.baslama_tarihi = datetime.strptime(
            proje_bilgileri["projeler-baslamatarihi-guncelle"], '%Y-%m-%d')
        proje.sure = proje_bilgileri["projeler-sure-guncelle"]
        proje.tamamlanma_tarihi = datetime.strptime(
            proje_bilgileri["projeler-tamamlanmatarihi-guncelle"], '%Y-%m-%d')
        if takip == "yok":
            proje_bilgileri["projeler-takiptarihi-guncelle"] = "2087-09-09"
        proje.takip_tarihi = datetime.strptime(
            proje_bilgileri["projeler-takiptarihi-guncelle"], '%Y-%m-%d')   
        proje.durum = proje_bilgileri["projeler-durum-guncelle"]
        db.session.commit()
        flash('Proje Verileriniz güncellenmiştir', 'primary')
        return redirect(url_for("main.projeleri_getir", program=program, durum=durum))
    else:
        flash('Veriler Alınamamıştır', 'danger')
        return redirect(url_for("main.projeleri_getir", program=program, durum=durum))


# ******* KOSGEB / Projeler ROUTINGS End *********#

@main.route('/baglantilar')
@login_required
def baglantilar():
    return render_template("baglantilar.html")


# ******* KOSGEB / Ödemeler ROUTINGS BEGIN *********#
@main.route('/odemeler/', defaults={'durum': "BEKLEMEDE", 'program': "Tüm Projeler", 'destek': "Tüm Destekler",
                                    'firm': "Tüm İşletmeler"})
@main.route('/odemeler/<durum>/<program>/<destek>/<firm>/')
@login_required
def odemeleri_getir(durum, program, destek, firm):
    defaults = dict(durum=durum, program=program, destek=destek, isletme=firm,
                    programlar=Program.query.all(), destekler=Destek.query.all())
    qfirm = firm + "%" if not firm == "Tüm İşletmeler" else "%"
    qprogram = program + "%" if not program == "Tüm Projeler" else "%"
    qdestek = destek + "%" if not destek == "Tüm Destekler" else "%"
    odemes = db.session.query(Isletme.unvan, Isletme.vergi, Proje.program_ismi, Odeme.id, Odeme.destek_ismi,
                              Odeme.karekod, Odeme.tarih, Odeme.tutar, Odeme.durum) \
        .select_from(Odeme) \
        .join(Proje) \
        .join(Isletme) \
        .filter(Odeme.durum.like(durum)) \
        .filter(Proje.program_ismi.like(qprogram)) \
        .filter(Odeme.destek_ismi.like(qdestek)) \
        .filter(Isletme.unvan.like(qfirm)) \
        .order_by(Odeme.tarih.desc()).all()
    return render_template("odemeler.html", odemeler=odemes, defaults=defaults)


@main.route('/odemeler/sorgu', methods=['POST', 'GET'])
def odeme_sorgulama():
    if request.method == 'POST':
        durum = request.form.get("odeme_durum_bilgisi")
        proje = request.form.get("odeme_proje_bilgisi")
        destek = request.form.get("odeme_destek_bilgisi")
        firm = request.form.get("odeme_isletme_bilgisi")
        if len(firm) < 2:
            firm = "Tüm İşletmeler"
        return redirect(url_for("main.odemeleri_getir", durum=durum, program=proje, destek=destek, firm=firm))


@main.route('/odemeler/<durum>/<program>/<destek>/<firm>/<int:odeme_id>/guncelle/', methods=["POST", "GET"])
def odeme_verisi_guncelle(durum, program, destek, firm, odeme_id):
    isimler = ["odeme-destek-guncelle", "odeme-destek-guncelle", "odeme-kadekod-guncelle",
               "odeme-tarih-guncelle", "odeme-tutar-guncelle", "odeme-durum-guncelle"]
    if request.method == 'POST':
        odeme_bilgileri = {isim: request.form.get(isim) for isim in isimler}
        odeme = Odeme.query.filter(Odeme.id == odeme_id).first()
        odeme.destek_ismi = odeme_bilgileri["odeme-destek-guncelle"]
        odeme.karekod = odeme_bilgileri["odeme-kadekod-guncelle"]
        odeme.destek_ismi = odeme_bilgileri["odeme-destek-guncelle"]
        odeme.tarih = datetime.strptime(
            odeme_bilgileri["odeme-tarih-guncelle"], '%Y-%m-%d')
        odeme.tutar = odeme_bilgileri["odeme-tutar-guncelle"]
        odeme.durum = odeme_bilgileri["odeme-durum-guncelle"]
        db.session.commit()
        flash('Ödeme Verileriniz güncellenmiştir', 'primary')
        return redirect(url_for("main.odemeleri_getir", durum=durum, program=program, destek=destek, firm=firm))
    else:
        flash('Veriler Alınamamıştır', 'danger')
        return redirect(url_for("main.odemeleri_getir", durum=durum, program=program, destek=destek, firm=firm))


@main.route('/odemeler/<durum>/<program>/<destek>/<firm>/<int:odeme_id>/sil/')
def odeme_verisi_sil(durum, program, destek, firm, odeme_id):
    odeme = Odeme.query.filter(Odeme.id == odeme_id).first()
    db.session.delete(odeme)
    db.session.commit()
    flash('Seçilen Ödeme Silinmiştir', 'success')
    return redirect(url_for("main.odemeleri_getir", durum=durum, program=program, destek=destek, firm=firm))


# ******* KOSGEB / Ödemeler ROUTINGS End *********#

# ******* KOSGEB / İşletmeler ROUTINGS Begin *********#


@main.route('/isletmeler-tablosu')
@login_required
def isletmeler():
    firm = Isletme.query.all()
    return render_template("isletmeler.html", isletmeler=firm)


@main.route('/isletmeler-tablosu/guncelle/<int:isletme_id>/', methods=["POST", "GET"])
def isletmeler_guncelle(isletme_id):
    isimler = ["adresguncelle", "beyyilguncelle",
               "bilgiguncelle", "durumguncelle"]
    if request.method == 'POST':
        isletme_bilgileri = {isim: request.form.get(isim) for isim in isimler}
        isletmes = Isletme.query.get(isletme_id)
        isletmes.adres = isletme_bilgileri["adresguncelle"]
        isletmes.bilgi = isletme_bilgileri["bilgiguncelle"]
        isletmes.durum = isletme_bilgileri["durumguncelle"]
        isletmes.bey_yil = isletme_bilgileri["beyyilguncelle"]
        db.session.commit()
        flash('İşletme Verileriniz güncellenmiştir', 'primary')
        return redirect(url_for("main.isletmeler"))
    else:
        flash('Veriler Alınamamıştır', 'danger')
        return redirect(url_for("main.isletmeler"))


# ******* KOSGEB / İşletmeler ROUTINGS End *********#


@main.route('/not-ekle', methods=["POST", "GET"])
def not_ekle():
    if request.method == 'POST':
        konu = request.form.get("not_konu_ekle")
        icerik = request.form.get("not_icerik_ekle")
        tarih = request.form.get("not_tarih_ekle")
        new_not = Notlar(konu=konu, icerik=icerik,
                         tarih=datetime.strptime(tarih, '%Y-%m-%d'), durum=0)
        db.session.add(new_not)
        db.session.commit()
        return redirect(url_for("main.index"))
    else:
        flash('Bağlantı Kurulamadı', 'danger')
        return redirect(url_for("main.index"))


@main.route('/not-sil/<int:not_id>')
def not_sil(not_id):
    noti = Notlar.query.filter(Notlar.id == not_id).first()
    db.session.delete(noti)
    db.session.commit()
    return redirect(url_for("main.index"))


@main.route('/not-tamamla/<int:not_id>')
def not_tamamlama(not_id):
    noti = Notlar.query.filter(Notlar.id == not_id).first()
    noti.durum = 1
    db.session.commit()
    return redirect(url_for("main.index"))


@main.route('/not-ekle2', methods=["POST", "GET"])
def not_ekle2():
    if request.method == 'POST':
        konu = request.form.get("not_konu_ekle")
        icerik = request.form.get("not_icerik_ekle")
        tarih = request.form.get("not_tarih_ekle")
        new_not = Notlar2(konu=konu, icerik=icerik,
                          tarih=datetime.strptime(tarih, '%Y-%m-%d'), durum=0)
        db.session.add(new_not)
        db.session.commit()
        return redirect(url_for("main.index"))
    else:
        flash('Bağlantı Kurulamadı', 'danger')
        return redirect(url_for("main.index"))


@main.route('/not-sil2/<int:not_id>')
def not_sil2(not_id):
    noti = Notlar2.query.filter(Notlar2.id == not_id).first()
    db.session.delete(noti)
    db.session.commit()
    return redirect(url_for("main.index"))


@main.route('/not-tamamla2/<int:not_id>')
def not_tamamlama2(not_id):
    noti = Notlar2.query.filter(Notlar2.id == not_id).first()
    noti.durum = 1
    db.session.commit()
    return redirect(url_for("main.index"))

# *************************************** KOSGEB ROUTINGS END ******************************************************* #
