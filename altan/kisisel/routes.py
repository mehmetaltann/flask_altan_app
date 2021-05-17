from flask import render_template, request, redirect, url_for, flash
from altan.kisisel import kisisel
from altan.extensions import db, login_required
from altan.models import Tarih, Gelir, Fatura, NakitGider, KrediKarti, Kitaplar, Filmler, Diziler, Yatirimlar, \
    YatirimAlislar, YatirimSatislar
from datetime import datetime


@kisisel.route('/hesap')
@login_required
def hesap():
    date = datetime.now()
    tarih = Tarih(id=9999, yil=date.year, ay=date.month)
    return render_template("hesap.html", tarih=tarih, gelir=None, fatura=None, kredi_karti=None,
                           nakit_gider=None, toplam_gider=0)


@kisisel.route('/hesap', methods=["POST"])
def tarih_verisi_al():
    yil = request.form.get("yil")
    ay = request.form.get("ay")
    tarih = Tarih.query.filter(Tarih.yil == yil).filter(Tarih.ay == ay).first()
    if tarih:
        return redirect(url_for("kisisel.hesap_verilerini_getir", tarih_id=tarih.id))
    else:
        flash('Bu aya ait veri bulunmamaktadır', 'danger')
        return redirect(url_for("kisisel.hesap_verisiz_getir", yil=yil, ay=ay))


@kisisel.route('/hesap/<int:yil>/<int:ay>')
@login_required
def hesap_verisiz_getir(yil, ay):
    tarih = Tarih(id=9997, ay=ay, yil=yil)
    return render_template("hesap.html", tarih=tarih, gelir=None, fatura=None, kredi_karti=None,
                           nakit_gider=None, toplam_gider=0)


@kisisel.route('/hesap/<int:tarih_id>')
@login_required
def hesap_verilerini_getir(tarih_id):
    tarih = Tarih.query.filter(Tarih.id == tarih_id).first()
    gelir = Gelir.query.filter(Gelir.tarih_id == tarih_id).first()
    fatura = Fatura.query.filter(Fatura.tarih_id == tarih_id).first()
    fatura_toplam = 0 if not fatura else fatura.toplam
    kredi_karti = KrediKarti.query.filter(KrediKarti.tarih_id == tarih_id).first()
    kredi_karti_toplam = 0 if not kredi_karti else kredi_karti.toplam
    nakit_gider = NakitGider.query.filter(NakitGider.tarih_id == tarih_id).first()
    nakit_gider_toplam = 0 if not nakit_gider else nakit_gider.toplam
    toplam_gider = round((fatura_toplam + kredi_karti_toplam + nakit_gider_toplam), 2)
    return render_template("hesap.html", tarih=tarih, gelir=gelir, fatura=fatura, kredi_karti=kredi_karti,
                           nakit_gider=nakit_gider, toplam_gider=toplam_gider)


@kisisel.route('/hesap/gelir-ekle/<int:tarih_yil>/<int:tarih_ay>', methods=["POST", "GET"])
def gelir_ekle(tarih_yil, tarih_ay):
    yil = tarih_yil
    ay = tarih_ay
    tarih = Tarih.query.filter(Tarih.yil == yil).filter(Tarih.ay == ay).first()
    gelir_isimleri = ["maas", "fon_satis", "gdiger", "gelir_aciklama"]
    if request.method == 'POST':
        gelirler = {gelir: request.form.get(gelir) for gelir in gelir_isimleri}
        for key in gelirler.keys():
            if not gelirler[key]:
                if gelirler[key] == "gelir_aciklama":
                    gelirler[key] = "NULL"
                else:
                    gelirler[key] = 0
        if tarih:
            gelir = Gelir.query.filter(Gelir.tarih_id == tarih.id).first()
            gelir.maas = gelirler["maas"]
            gelir.fon_satis = gelirler["fon_satis"]
            gelir.gdiger = gelirler["gdiger"]
            gelir.aciklama = gelirler["gelir_aciklama"]
            flash('Verileriniz güncellenmiştir', 'primary')
            db.session.commit()
        else:
            tarih = Tarih(yil=yil, ay=ay)
            db.session.add(tarih)
            db.session.commit()
            gelir = Gelir(tarih_id=tarih.id, maas=gelirler["maas"], fon_satis=gelirler["fon_satis"],
                          gdiger=gelirler["gdiger"], aciklama=gelirler["aciklama"])
            db.session.add(gelir)
            db.session.commit()
            new_kredi_karti = KrediKarti(tarih_id=tarih.id, market=0, araba=0, giyim=0, hazir_yemek=0, saglik=0,
                                         mobilya=0, egitim=0, kdiger=0)
            db.session.add(new_kredi_karti)
            db.session.commit()
            new_nakit_gider = NakitGider(tarih_id=tarih.id, atm=0, kira=0, aidat=0, yakit=0,
                                         bes=0, fon_alim=0, ndiger=0, aciklama="")
            db.session.add(new_nakit_gider)
            db.session.commit()
            new_fatura = Fatura(tarih_id=tarih.id, elektrik=0, su=0, dogalgaz=0, tv_internet=0, tel_mehmet=0,
                                tel_sena=0)
            db.session.add(new_fatura)
            db.session.commit()
            flash('Yeni kayıt eklenmiştir', 'success')
    else:
        flash('veriler alınamamıştır', 'danger')
    return redirect(url_for("kisisel.hesap_verilerini_getir", tarih_id=tarih.id))


@kisisel.route('/hesap/gider-ekle<int:tarih_yil>/<int:tarih_ay>', methods=["POST", "GET"])
def gider_ekle(tarih_yil, tarih_ay):
    yil = tarih_yil
    ay = tarih_ay
    tarih = Tarih.query.filter(Tarih.yil == yil).filter(Tarih.ay == ay).first()
    kredi_karti_isimleri = ["market", "araba", "giyim", "hazir_yemek",
                            "saglik", "mobilya", "egitim", "kredi_karti_diger"]
    nakit_giderler_isimleri = ["atm_nakit", "kira", "aidat", "yakit",
                               "bes", "fon_alim", "nakit_gider_diger", "nakit_gider_aciklama"]
    fatura_isimleri = ["elektrik", "su", "dogalgaz", "gider_tv_internet", "mehmet_tel", "sena_tel"]
    if request.method == 'POST':
        kredi_karti_dic = {gider: request.form.get(gider) for gider in kredi_karti_isimleri}
        for key in kredi_karti_dic.keys():
            if not kredi_karti_dic[key]:
                kredi_karti_dic[key] = 0
        nakit_giderler_dic = {gider: request.form.get(gider) for gider in nakit_giderler_isimleri}
        for key in nakit_giderler_dic.keys():
            if not nakit_giderler_dic[key]:
                if nakit_giderler_dic[key] == "nakit_gider_aciklama":
                    nakit_giderler_dic[key] = "NULL"
                else:
                    nakit_giderler_dic[key] = 0
        fatura_dic = {gider: request.form.get(gider) for gider in fatura_isimleri}
        for key in fatura_dic.keys():
            if not fatura_dic[key]:
                fatura_dic[key] = 0
        if tarih:
            kredi_karti = KrediKarti.query.filter(KrediKarti.tarih_id == tarih.id).first()
            nakit_gider = NakitGider.query.filter(NakitGider.tarih_id == tarih.id).first()
            fatura = Fatura.query.filter(Fatura.tarih_id == tarih.id).first()
            kredi_karti.market = kredi_karti_dic["market"]
            kredi_karti.araba = kredi_karti_dic["araba"]
            kredi_karti.giyim = kredi_karti_dic["giyim"]
            kredi_karti.hazir_yemek = kredi_karti_dic["hazir_yemek"]
            kredi_karti.saglik = kredi_karti_dic["saglik"]
            kredi_karti.mobilya = kredi_karti_dic["mobilya"]
            kredi_karti.egitim = kredi_karti_dic["egitim"]
            kredi_karti.kdiger = kredi_karti_dic["kredi_karti_diger"]
            # Nakit Giderler
            nakit_gider.atm = nakit_giderler_dic["atm_nakit"]
            nakit_gider.kira = nakit_giderler_dic["kira"]
            nakit_gider.aidat = nakit_giderler_dic["aidat"]
            nakit_gider.yakit = nakit_giderler_dic["yakit"]
            nakit_gider.bes = nakit_giderler_dic["bes"]
            nakit_gider.fon_alim = nakit_giderler_dic["fon_alim"]
            nakit_gider.ndiger = nakit_giderler_dic["nakit_gider_diger"]
            nakit_gider.aciklama = nakit_giderler_dic["nakit_gider_aciklama"]
            # Faturalar
            fatura.elektrik = fatura_dic["elektrik"]
            fatura.su = fatura_dic["su"]
            fatura.dogalgaz = fatura_dic["dogalgaz"]
            fatura.tv_internet = fatura_dic["gider_tv_internet"]
            fatura.tel_mehmet = fatura_dic["mehmet_tel"]
            fatura.tel_sena = fatura_dic["sena_tel"]
            flash('Verileriniz güncellenmiştir', 'primary')
            db.session.commit()
        else:
            tarih = Tarih(yil=yil, ay=ay)
            db.session.add(tarih)
            db.session.commit()
            new_kredi_karti = KrediKarti(tarih_id=tarih.id, market=kredi_karti_dic["market"],
                                         araba=kredi_karti_dic["araba"], giyim=kredi_karti_dic["giyim"],
                                         hazir_yemek=kredi_karti_dic["hazir_yemek"], saglik=kredi_karti_dic["saglik"],
                                         mobilya=kredi_karti_dic["mobilya"],
                                         egitim=kredi_karti_dic["egitim"], kdiger=kredi_karti_dic["kredi_karti_diger"])
            db.session.add(new_kredi_karti)
            db.session.commit()
            new_nakit_gider = NakitGider(tarih_id=tarih.id, atm=nakit_giderler_dic["atm_nakit"],
                                         kira=nakit_giderler_dic["kira"], aidat=nakit_giderler_dic["aidat"],
                                         yakit=nakit_giderler_dic["yakit"], bes=nakit_giderler_dic["bes"],
                                         fon_alim=nakit_giderler_dic["fon_alim"],
                                         ndiger=nakit_giderler_dic["nakit_gider_diger"],
                                         aciklama=nakit_giderler_dic["nakit_gider_aciklama"])
            db.session.add(new_nakit_gider)
            db.session.commit()
            new_fatura = Fatura(tarih_id=tarih.id, elektrik=fatura_dic["elektrik"], su=fatura_dic["su"],
                                dogalgaz=fatura_dic["dogalgaz"],
                                tv_internet=fatura_dic["gider_tv_internet"], tel_mehmet=fatura_dic["mehmet_tel"],
                                tel_sena=fatura_dic["sena_tel"])
            db.session.add(new_fatura)
            db.session.commit()
            new_gelir = Gelir(tarih_id=tarih.id, maas=0, fon_satis=0, gdiger=0, aciklama="")
            db.session.add(new_gelir)
            db.session.commit()
            flash('Yeni veriler eklenmiştir', 'success')

        return redirect(url_for("kisisel.hesap_verilerini_getir", tarih_id=tarih.id))


@kisisel.route('/butce_sorgu/')
@login_required
def butce_sorgu():
    defaults = {'bas_yil': 2020, 'bit_yil': 2020, 'gelir_sor': "Tümü", 'gider_sor': "Tümü",
                "yillar": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021],
                "ay_sayisi": [], "gelir_tablo": [], "gider_tablo": [], "toplam_gelir": 0, "toplam_gider": 0,
                "gelir_ort": 0, "gider_ort": 0}
    gelirler = ["toplam", "maas", "gdiger", "fon_satis"]
    gelirs = ["Tümü", "Maaş", "Diğer Gelirler", "Fon Satış"]
    giderler = ["Tümü", "Kredi Kartı", "market", "araba", "giyim", "hazir_yemek", "saglik", "mobilya",
                "egitim", "kdiger", "Faturalar", "elektrik", "su", "dogalgaz", "tv_internet", "tel_mehmet",
                "tel_sena", "Nakit Giderler", "atm", "kira", "aidat", "yakit", "bes", "fon_alim", "ndiger"]
    giders = ["Tümü", "Kredi Kartı", "Market", "Araç", "Giyim", "Hazır Yemek", "Saglık", "Ev Eşyası",
              "Eğitim - Teknoloji", "Kredi Kartı Diğer", "Faturalar", "Elektrik", "Su", "Doğalgaz", "Tv - İnternet",
              "Mehmet Telefon", "Sena Telefon", "Nakit Giderler", "ATM Para Çekme", "Kira", "Aidat", "Yakıt",
              "Bireysel Emeklilik", "Fon Alımı", "Diğer Nakit"]

    return render_template("butce_sorgu.html", packed_gelirler=zip(gelirler, gelirs),
                           packed_giderler=zip(giderler, giders),
                           giderler=giderler, defaults=defaults)


@kisisel.route('/butce_sorgu', methods=['POST', 'GET'])
def butce_sorgula():
    if request.method == 'POST':
        bas_yil = request.form.get("baslangic_yil")
        bit_yil = request.form.get("bitis_yil")
        gelir_sor = request.form.get("gelir-sorgu")
        gider_sor = request.form.get("gider-sorgu")
        if bas_yil > bit_yil:
            flash('Başlangıç Tarihi, Bitiş Tarihinden Küçük Olamaz', 'danger')
            return redirect(url_for("kisisel.butce_sorgu"))
        else:
            return redirect(url_for("kisisel.butce_sorgu_getir", bas_yil=bas_yil, bit_yil=bit_yil, gelir_sor=gelir_sor,
                                    gider_sor=gider_sor))
    else:
        flash('Veriler Alınamamıştır', 'danger')
        return redirect(url_for("kisisel.butce_sorgu"))


@kisisel.route('/butce_sorgu/<int:bas_yil>/<int:bit_yil>/<string:gelir_sor>/<string:gider_sor>/')
@login_required
def butce_sorgu_getir(bas_yil, bit_yil, gelir_sor, gider_sor):
    defaults = {'bas_yil': bas_yil, 'bit_yil': bit_yil, 'gelir_sor': gelir_sor, 'gider_sor': gider_sor,
                "yillar": [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021],
                "ay_sayisi": [], "gelir_tablo": [], "gider_tablo": [], "toplam_gelir": 0, "toplam_gider": 0,
                "gelir_ort": 0, "gider_ort": 0}
    gelirler = ["toplam", "maas", "gdiger", "fon_satis"]
    gelirs = ["Tümü", "Maaş", "Diğer Gelirler", "Fon Satış"]
    giderler = ["Tümü", "Kredi Kartı", "market", "araba", "giyim", "hazir_yemek", "saglik", "mobilya",
                "egitim", "kdiger", "Faturalar", "elektrik", "su", "dogalgaz", "tv_internet", "tel_mehmet",
                "tel_sena", "Nakit Giderler", "atm", "kira", "aidat", "yakit", "bes", "fon_alim", "ndiger"]
    giders = ["Tümü", "Kredi Kartı", "Market", "Araç", "Giyim", "Hazır Yemek", "Saglık", "Ev Eşyası",
              "Eğitim - Teknoloji", "Kredi Kartı Diğer", "Faturalar", "Elektrik", "Su", "Doğalgaz", "Tv - İnternet",
              "Mehmet Telefon", "Sena Telefon", "Nakit Giderler", "ATM Para Çekme", "Kira", "Aidat", "Yakıt",
              "Bireysel Emeklilik", "Fon Alımı", "Diğer Nakit"]
    toplam_gelir = 0
    toplam_gider = 0
    if bas_yil == bit_yil:
        tarihler = Tarih.query.filter(Tarih.yil == bas_yil).all()
    else:
        tarihler = Tarih.query.filter(Tarih.yil.between(bas_yil, bit_yil))
    for i, tarih in enumerate(tarihler):
        defaults["ay_sayisi"].append(i + 1)
        for gelir in tarih.gelirler:
            gelir_kalemi = getattr(gelir, gelir_sor)
            toplam_gelir += gelir_kalemi
            defaults["toplam_gelir"] = round(toplam_gelir, 2)
            defaults["gelir_tablo"].append(gelir_kalemi)
            defaults["gelir_ort"] = round((toplam_gelir / len(defaults["ay_sayisi"])), 2)
        if gider_sor == "Tümü":
            for gider1, gider2, gider3 in zip(tarih.kredi_karti, tarih.faturalar, tarih.nakit_gider):
                gider_kalemi = gider1.toplam + gider2.toplam + gider3.toplam
                toplam_gider += gider_kalemi
                defaults["gider_tablo"].append(gider_kalemi)
        elif gider_sor in giderler[1:10]:
            for gider in tarih.kredi_karti:
                if gider_sor == "Kredi Kartı":
                    gider_kalemi = getattr(gider, "toplam")
                else:
                    gider_kalemi = getattr(gider, gider_sor)
                toplam_gider += gider_kalemi
                defaults["gider_tablo"].append(gider_kalemi)
        elif gider_sor in giderler[10:17]:
            for gider in tarih.faturalar:
                if gider_sor == "Faturalar":
                    gider_kalemi = getattr(gider, "toplam")
                else:
                    gider_kalemi = getattr(gider, gider_sor)
                toplam_gider += gider_kalemi
                defaults["gider_tablo"].append(gider_kalemi)
        elif gider_sor in giderler[17:25]:
            for gider in tarih.nakit_gider:
                if gider_sor == "Nakit Giderler":
                    gider_kalemi = getattr(gider, "toplam")
                else:
                    gider_kalemi = getattr(gider, gider_sor)
                toplam_gider += gider_kalemi
                defaults["gider_tablo"].append(gider_kalemi)
        defaults["toplam_gider"] = round(toplam_gider, 2)
        defaults["gider_ort"] = round((toplam_gider / len(defaults["ay_sayisi"])), 2)
    return render_template("butce_sorgu.html", packed_gelirler=zip(gelirler, gelirs),
                           packed_giderler=zip(giderler, giders), defaults=defaults)


@kisisel.route('/kitaplar')
@login_required
def kitaplar():
    kitaps = Kitaplar.query.all()
    return render_template("kitaplar.html", kitaplar=kitaps)


@kisisel.route('/kitaplar/ekle//', methods=['POST', 'GET'])
def kitap_ekle():
    isimler = ["kitapisbnekle", "kitapisimekle", "kitapyazarekle", "kitapturekle",
               "kitapyayinbilgisiekle", "kitapalinmayeriekle", "kitapalinmatarihiekle", "kitapokunmadurumuekle"]
    if request.method == 'POST':
        kitap_bilgileri = {isim: request.form.get(isim) for isim in isimler}
        new_kitap = Kitaplar(isim=kitap_bilgileri["kitapisimekle"], isbn=kitap_bilgileri["kitapisbnekle"],
                             tur=kitap_bilgileri["kitapturekle"], yazar=kitap_bilgileri["kitapyazarekle"],
                             yayin_bilgisi=kitap_bilgileri["kitapyayinbilgisiekle"],
                             alinma_yeri=kitap_bilgileri["kitapalinmayeriekle"],
                             alinma_tarihi=datetime.strptime(kitap_bilgileri["kitapalinmatarihiekle"], '%Y-%m-%d'),
                             okunma_durumu=kitap_bilgileri["kitapokunmadurumuekle"])
        db.session.add(new_kitap)
        db.session.commit()
        flash('Kitap Veritabanına Eklenmiştir', 'success')
        return redirect(url_for("kisisel.kitaplar"))
    else:
        flash('Kitap Verileri Eklenemedi', 'danger')
        return redirect(url_for("kisisel.kitaplar"))


@kisisel.route('/kitaplar/guncelle/<int:kitap_id>/', methods=['POST', 'GET'])
def kitap_guncelle(kitap_id):
    isimler = ["kitapisbnguncelle", "kitapisimguncelle", "kitapyazarguncelle", "kitapturguncelle",
               "kitapyayinbilgisiguncelle", "kitapalinmayeriguncelle", "kitapalinmatarihiguncelle",
               "kitapokunmadurumuguncelle"]
    if request.method == 'POST':
        kitap_bilgileri = {isim: request.form.get(isim) for isim in isimler}
        kitap = Kitaplar.query.filter(Kitaplar.id == kitap_id).first()
        kitap.isbn = kitap_bilgileri["kitapisbnguncelle"]
        kitap.isim = kitap_bilgileri["kitapisimguncelle"]
        kitap.yazar = kitap_bilgileri["kitapyazarguncelle"]
        kitap.tur = kitap_bilgileri["kitapturguncelle"]
        kitap.yayin_bilgisi = kitap_bilgileri["kitapyayinbilgisiguncelle"]
        kitap.alinma_yeri = kitap_bilgileri["kitapalinmayeriguncelle"]
        kitap.alinma_tarihi = datetime.strptime(kitap_bilgileri["kitapalinmatarihiguncelle"], '%Y-%m-%d')
        kitap.okunma_durumu = kitap_bilgileri["kitapokunmadurumuguncelle"]
        db.session.commit()
        flash('Kitap Verileri Güncellenmiştir.', 'success')
        return redirect(url_for("kisisel.kitaplar"))
    else:
        flash('Kitap Verileri Güncellenemedi', 'danger')
        return redirect(url_for("kisisel.kitaplar"))


@kisisel.route('/kitaplar/sil/<int:kitap_id>/')
def kitap_sil(kitap_id):
    kitap = Kitaplar.query.filter(Kitaplar.id == kitap_id).first()
    db.session.delete(kitap)
    db.session.commit()
    flash('Seçilen Kitap Veritabanından Silinmiştir', 'success')
    return redirect(url_for("kisisel.kitaplar"))


@kisisel.route('/diziler')
@login_required
def diziler():
    dizis = Diziler.query.all()
    return render_template("diziler.html", diziler=dizis)


@kisisel.route('/diziler/ekle/', methods=['POST', 'GET'])
def dizi_ekle():
    isimler = ["diziisimekle", "dizicikistarihiekle", "diziturekle", "dizisonizlenenekle",
               "diziimdbpuaniekle", "diziimdblinkekle", "dizipuanimekle", "dizidurumekle"]
    if request.method == 'POST':
        dizi_bilgileri = {isim: request.form.get(isim) for isim in isimler}
        new_dizi = Diziler(isim=dizi_bilgileri["diziisimekle"], tur=dizi_bilgileri["diziturekle"],
                           cikis_tarihi=dizi_bilgileri["dizicikistarihiekle"],
                           son_izlenen=dizi_bilgileri["dizisonizlenenekle"],
                           imdb_puani=dizi_bilgileri["diziimdbpuaniekle"], imdb_link=dizi_bilgileri["diziimdblinkekle"],
                           mehmet_puan=dizi_bilgileri["dizipuanimekle"], ddurum=dizi_bilgileri["dizidurumekle"])
        db.session.add(new_dizi)
        db.session.commit()
        flash('Dizi Veritabanına Eklenmiştir', 'success')
        return redirect(url_for("kisisel.diziler"))
    else:
        flash('Dizi Verileri Eklenemedi', 'danger')
        return redirect(url_for("kisisel.diziler"))


@kisisel.route('/diziler/guncelle/<int:dizi_id>/', methods=['POST', 'GET'])
def dizi_guncelle(dizi_id):
    isimler = ["diziisimguncelle", "dizicikistarihiguncelle", "diziturguncelle", "dizisonizlenenguncelle",
               "diziimdbpuaniguncelle", "diziimdblinkguncelle", "dizipuanimguncelle", "dizidurumguncelle"]
    if request.method == 'POST':
        dizi_bilgileri = {isim: request.form.get(isim) for isim in isimler}
        dizi = Diziler.query.filter(Diziler.id == dizi_id).first()
        dizi.isim = dizi_bilgileri["diziisimguncelle"]
        dizi.tur = dizi_bilgileri["diziturguncelle"]
        dizi.cikis_tarihi = dizi_bilgileri["dizicikistarihiguncelle"]
        dizi.son_izlenen = dizi_bilgileri["dizisonizlenenguncelle"]
        dizi.imdb_puani = dizi_bilgileri["diziimdbpuaniguncelle"]
        dizi.imdb_link = dizi_bilgileri["diziimdblinkguncelle"]
        dizi.mehmet_puan = dizi_bilgileri["dizipuanimguncelle"]
        dizi.ddurum = dizi_bilgileri["dizidurumguncelle"]
        db.session.commit()
        flash('Dizi Verileri Güncellenmiştir.', 'success')
        return redirect(url_for("kisisel.diziler"))
    else:
        flash('Dizi Verileri Güncellenemedi', 'danger')
        return redirect(url_for("kisisel.diziler"))


@kisisel.route('/diziler/sil/<int:dizi_id>/')
def dizi_sil(dizi_id):
    dizi = Diziler.query.filter(Diziler.id == dizi_id).first()
    db.session.delete(dizi)
    db.session.commit()
    flash('Seçilen Dizi Veritabanından Silinmiştir', 'success')
    return redirect(url_for("kisisel.diziler"))


@kisisel.route('/filmler')
@login_required
def filmler():
    films = Filmler.query.all()
    return render_template("filmler.html", filmler=films)


@kisisel.route('/filmler/ekle/', methods=['POST', 'GET'])
def film_ekle():
    isimler = ["filmisimekle", "filmvizyonekle", "filmturekle", "filmyonetmenekle",
               "filmimdbpuaniekle", "filmimdblinkekle", "filmpuanimekle"]
    if request.method == 'POST':
        film_bilgileri = {isim: request.form.get(isim) for isim in isimler}
        new_film = Filmler(isim=film_bilgileri["filmisimekle"], tur=film_bilgileri["filmturekle"],
                           cikis_tarihi=film_bilgileri["filmvizyonekle"], yonetmen=film_bilgileri["filmyonetmenekle"],
                           imdb_puani=film_bilgileri["filmimdbpuaniekle"], imdb_link=film_bilgileri["filmimdblinkekle"],
                           mehmet_puan=film_bilgileri["filmpuanimekle"])
        db.session.add(new_film)
        db.session.commit()
        flash('Film Veritabanına Eklenmiştir', 'success')
        return redirect(url_for("kisisel.filmler"))
    else:
        flash('Film Verileri Eklenemedi', 'danger')
        return redirect(url_for("kisisel.filmler"))


@kisisel.route('/filmler/<int:film_id>/guncelle/', methods=['POST', 'GET'])
def film_guncelle(film_id):
    isimler = ["filmisimguncelle", "filmvizyonguncelle", "filmturguncelle", "filmyonetmenguncelle",
               "filmimdbpuaniguncelle", "filmimdblinkguncelle", "filmpuanimguncelle"]
    if request.method == 'POST':
        film_bilgileri = {isim: request.form.get(isim) for isim in isimler}
        film = Filmler.query.filter(Filmler.id == film_id).first()
        film.isim = film_bilgileri["filmisimguncelle"]
        film.tur = film_bilgileri["filmturguncelle"]
        film.cikis_tarihi = film_bilgileri["filmvizyonguncelle"]
        film.yonetmen = film_bilgileri["filmyonetmenguncelle"]
        film.imdb_puani = film_bilgileri["filmimdbpuaniguncelle"]
        film.imdb_link = film_bilgileri["filmimdblinkguncelle"]
        film.mehmet_puan = film_bilgileri["filmpuanimguncelle"]
        db.session.commit()
        flash('Filmin Verileri Güncellenmiştir.', 'success')
        return redirect(url_for("kisisel.filmler"))
    else:
        flash('Film Verileri Güncellenemedi', 'danger')
        return redirect(url_for("kisisel.filmler"))


@kisisel.route('/filmler/<int:film_id>/sil/')
def film_sil(film_id):
    film = Filmler.query.filter(Filmler.id == film_id).first()
    db.session.delete(film)
    db.session.commit()
    flash('Seçilen Film Veritabanından Silinmiştir', 'success')
    return redirect(url_for("kisisel.filmler"))


@kisisel.route('/yatirim')
def yatirim():
    yatirimlar = Yatirimlar.query.filter(Yatirimlar.durum.like("Aktif")).all()
    tum_yatirimlar = Yatirimlar.query.all()

    def birim_fiyat(tur, kisa):
        if not tur == "Fon":
            if tur == "Altın":
                kisa = "GA"
            from urllib.request import urlopen
            import json
            doviz_url = "https://api.genelpara.com/embed/para-birimleri.json"
            bir_fiyat = float(json.loads(urlopen(doviz_url).read().decode("utf-8"))[kisa]['alis'])
            if kisa == "BTC":
                dolar_birim = float(json.loads(urlopen(doviz_url).read().decode("utf-8"))["USD"]['alis'])
                bir_fiyat *= dolar_birim
        else:
            from bs4 import BeautifulSoup
            from requests import get
            fon_url = "https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod="
            fon_sayfa = BeautifulSoup(get(fon_url + kisa).text, "html.parser")
            bir_fiyat = float(fon_sayfa.select('.top-list span')[0].get_text().replace(",", "."))
        return bir_fiyat

    for yatir in yatirimlar:
        birim = birim_fiyat(yatir.tur, yatir.kisa)
        yatir.birim_fiyat = birim

    return render_template("yatirim.html", yatirimlar=yatirimlar, tum_yatirimlar=tum_yatirimlar)


@kisisel.route('/yatirim/ekle', methods=['POST', 'GET'])
def yatirim_ekle():
    isimler = ["yatirimturekle", "yatirimisimekle", "yatirimkisaekle",
               "yatirimbirimekle", "yatirimriskekle", "yatirimresimekle", "yatirimdurumekle"]
    if request.method == 'POST':
        yatirim_bilgileri = {isim: request.form.get(isim) for isim in isimler}
        new_yatirim = Yatirimlar(tur=yatirim_bilgileri["yatirimturekle"], isim=yatirim_bilgileri["yatirimisimekle"],
                                 kisa=yatirim_bilgileri["yatirimkisaekle"], birim=yatirim_bilgileri["yatirimbirimekle"],
                                 risk=yatirim_bilgileri["yatirimriskekle"], resim=yatirim_bilgileri["yatirimresimekle"],
                                 durum=yatirim_bilgileri["yatirimdurumekle"], birim_fiyat=0)
        db.session.add(new_yatirim)
        db.session.commit()
        flash('Yeni Yatırım Veritabanına Eklenmiştir', 'success')
        return redirect(url_for("kisisel.yatirim"))
    else:
        flash('Veriler Eklenemedi', 'danger')
        return redirect(url_for("kisisel.yatirim"))


@kisisel.route('/yatirim/kaldir', methods=['POST', 'GET'])
def yatirim_kaldir():
    if request.method == 'POST':
        yatirim_kisa = request.form.get("yatirimadi")
        yatirim_d = Yatirimlar.query.filter(Yatirimlar.kisa == yatirim_kisa).first()
        yatirim_d.durum = "Pasif"
        db.session.commit()
        flash('Yatırım Kaldırıldı', 'success')
        return redirect(url_for("kisisel.yatirim"))


@kisisel.route('/yatirim/getir', methods=['POST', 'GET'])
def yatirim_getir():
    if request.method == 'POST':
        yatirim_kisa = request.form.get("yatirimadi2")
        yatirim_d = Yatirimlar.query.filter(Yatirimlar.kisa == yatirim_kisa).first()
        yatirim_d.durum = "Aktif"
        db.session.commit()
        flash('Yatırım Getirildi', 'success')
        return redirect(url_for("kisisel.yatirim"))


@kisisel.route('/yatirim/alis-ekle', methods=['POST', 'GET'])
def yatirim_alis_ekle():
    isimler = ["yatirimalisyatirimekle", "yatirimalistarihekle",
               "yatirimalismiktarekle", "yatirimalisfiyatekle"]
    if request.method == 'POST':
        alis_bilgileri = {isim: request.form.get(isim) for isim in isimler}
        new_alis = YatirimAlislar(yatirim=alis_bilgileri["yatirimalisyatirimekle"],
                                  tarih=datetime.strptime(alis_bilgileri["yatirimalistarihekle"], '%Y-%m-%d'),
                                  miktar=alis_bilgileri["yatirimalismiktarekle"],
                                  birim_fiyat=alis_bilgileri["yatirimalisfiyatekle"])
        db.session.add(new_alis)
        db.session.commit()
        flash(f'{alis_bilgileri["yatirimalisyatirimekle"]} Alışı Veritabanına Eklenmiştir', 'success')
        return redirect(url_for("kisisel.yatirim"))
    else:
        flash('Alış Verileri Güncellenemedi', 'danger')
        return redirect(url_for("kisisel.yatirim"))


@kisisel.route('/yatirim/alis-guncelle/<int:alis_id>/', methods=['POST', 'GET'])
def yatirim_alis_guncelle(alis_id):
    isimler = ["yatirimalistarihguncelle", "yatirimalismiktarguncelle", "yatirimalisfiyatguncelle"]
    if request.method == 'POST':
        alis_bilgileri = {isim: request.form.get(isim) for isim in isimler}
        alis = YatirimAlislar.query.filter(YatirimAlislar.id == alis_id).first()
        alis.tarih = datetime.strptime(alis_bilgileri["yatirimalistarihguncelle"], '%Y-%m-%d')
        alis.miktar = alis_bilgileri["yatirimalismiktarguncelle"]
        alis.birim_fiyat = alis_bilgileri["yatirimalisfiyatguncelle"]
        db.session.commit()
        flash('Alış Güncellenmiştir.', 'success')
        return redirect(url_for("kisisel.yatirim"))
    else:
        flash('Alış Güncellenemedi', 'danger')
        return redirect(url_for("kisisel.yatirim"))


@kisisel.route('/yatirim/alis-sil/<int:alis_id>/')
def yatirim_alis_sil(alis_id):
    alis = YatirimAlislar.query.filter(YatirimAlislar.id == alis_id).first()
    db.session.delete(alis)
    db.session.commit()
    flash('Seçilen Alım Veritabanından Silinmiştir', 'success')
    return redirect(url_for("kisisel.yatirim"))


@kisisel.route('/yatirim/satis-ekle', methods=['POST', 'GET'])
def yatirim_satis_ekle():
    isimler = ["yatirimsatisyatirimekle", "yatirimsatistarihekle",
               "yatirimsatismiktarekle", "yatirimsatisfiyatekle"]
    if request.method == 'POST':
        satis_bilgileri = {isim: request.form.get(isim) for isim in isimler}
        new_satis = YatirimSatislar(yatirim=satis_bilgileri["yatirimsatisyatirimekle"],
                                    tarih=datetime.strptime(satis_bilgileri["yatirimsatistarihekle"], '%Y-%m-%d'),
                                    miktar=satis_bilgileri["yatirimsatismiktarekle"],
                                    birim_fiyat=satis_bilgileri["yatirimsatisfiyatekle"])
        db.session.add(new_satis)
        db.session.commit()
        flash(f'{satis_bilgileri["yatirimsatisyatirimekle"]} Satışı Eklenmiştir', 'success')
        return redirect(url_for("kisisel.yatirim"))
    else:
        flash('Film Verileri Güncellenemedi', 'danger')
        return redirect(url_for("kisisel.yatirim"))


@kisisel.route('/yatirim/satis-guncelle/<int:satis_id>/', methods=['POST', 'GET'])
def yatirim_satis_guncelle(satis_id):
    isimler = ["yatirimsatistarihguncelle", "yatirimsatismiktarguncelle", "yatirimsatisfiyatguncelle"]
    if request.method == 'POST':
        satis_bilgileri = {isim: request.form.get(isim) for isim in isimler}
        satis = YatirimSatislar.query.filter(YatirimSatislar.id == satis_id).first()
        satis.tarih = datetime.strptime(satis_bilgileri["yatirimsatistarihguncelle"], '%Y-%m-%d')
        satis.miktar = satis_bilgileri["yatirimsatismiktarguncelle"]
        satis.birim_fiyat = satis_bilgileri["yatirimsatisfiyatguncelle"]
        db.session.commit()
        flash('Satış Güncellenmiştir.', 'success')
        return redirect(url_for("kisisel.yatirim"))
    else:
        flash('Satış Güncellenemedi', 'danger')
        return redirect(url_for("kisisel.yatirim"))


@kisisel.route('/yatirim/satis-sil/<int:satis_id>/')
def yatirim_satis_sil(satis_id):
    satis = YatirimSatislar.query.filter(YatirimSatislar.id == satis_id).first()
    db.session.delete(satis)
    db.session.commit()
    flash('Seçilen Satış Veritabanından Silinmiştir', 'success')
    return redirect(url_for("kisisel.yatirim"))
