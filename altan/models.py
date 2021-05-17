from altan.extensions import db


class Isletme(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    vergi = db.Column(db.String(15), nullable=False, unique=True)
    unvan = db.Column(db.String(120), nullable=False, unique=True)
    sektor_ismi = db.Column(db.String(150), db.ForeignKey('sektor.isim'), nullable=False)
    tur = db.Column(db.String(8))
    tel1 = db.Column(db.Integer)
    tel2 = db.Column(db.Integer)
    mail = db.Column(db.String(45), nullable=False)
    yetkili = db.Column(db.String(30))
    adres = db.Column(db.String(70), nullable=False)
    bilgi = db.Column(db.String(30))
    bey_yil = db.Column(db.Integer)
    bey_cal = db.Column(db.String(5))
    bey_sat = db.Column(db.Float)
    durum = db.Column(db.String(15))
    projeler = db.relationship('Proje', backref='isletme')


class Proje(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    isletme_id = db.Column(db.Integer, db.ForeignKey('isletme.id'), nullable=False)
    program_ismi = db.Column(db.String(150), db.ForeignKey('program.isim'), nullable=False)
    baslama_tarihi = db.Column(db.Date, nullable=False)
    sure = db.Column(db.Integer)
    tamamlanma_tarihi = db.Column(db.Date)
    takip_tarihi = db.Column(db.Date)
    izleyici = db.Column(db.String(30))
    koordinator = db.Column(db.String(30))
    durum = db.Column(db.String(30))
    notlar = db.Column(db.String(50))
    izleme = db.Column(db.String(12))
    odemeler = db.relationship('Odeme', backref='proje')

    @property
    def odeme_toplami(self):
        toplam_odeme = 0
        if self.odemeler:
            for odeme in self.odemeler:
                toplam_odeme += odeme.tutar
        return round(toplam_odeme, 2)


class Odeme(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    karekod = db.Column(db.String(10), nullable=False)
    tutar = db.Column(db.Float, nullable=False)
    tarih = db.Column(db.Date, nullable=False)
    durum = db.Column(db.String(30), nullable=False)
    proje_id = db.Column(db.Integer, db.ForeignKey('proje.id'), nullable=False)
    destek_ismi = db.Column(db.String(150), db.ForeignKey('destek.isim'), nullable=False)


class Destek(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    isim = db.Column(db.String(150), nullable=False)
    odemeler = db.relationship('Odeme', backref='destek')


class Program(db.Model):
    id = db.Column(db.Integer, nullable=False, unique=True)
    isim = db.Column(db.String(150), primary_key=True, nullable=False)
    projeler = db.relationship('Proje', backref='program')


class Sektor(db.Model):
    isim = db.Column(db.String(150), primary_key=True, nullable=False)
    isletmeler = db.relationship('Isletme', backref='sektor')


class Gelir(db.Model):
    tarih_id = db.Column(db.Integer, db.ForeignKey('tarih.id'), primary_key=True, nullable=False)
    maas = db.Column(db.Float)
    fon_satis = db.Column(db.Float)
    gdiger = db.Column(db.Float)
    aciklama = db.Column(db.String(100))

    @property
    def toplam(self):
        toplam = round((self.maas + self.fon_satis + self.gdiger), 2)
        return toplam


class Fatura(db.Model):
    tarih_id = db.Column(db.Integer, db.ForeignKey('tarih.id'), primary_key=True, nullable=False)
    elektrik = db.Column(db.Float)
    su = db.Column(db.Float)
    dogalgaz = db.Column(db.Float)
    tv_internet = db.Column(db.Float)
    tel_mehmet = db.Column(db.Float)
    tel_sena = db.Column(db.Float)

    @property
    def toplam(self):
        toplam = round((self.elektrik + self.su + self.dogalgaz + self.tv_internet + self.tel_mehmet + self.tel_sena),
                       2)
        return toplam


class KrediKarti(db.Model):
    tarih_id = db.Column(db.Integer, db.ForeignKey('tarih.id'), primary_key=True, nullable=False)
    market = db.Column(db.Float)
    araba = db.Column(db.Float)
    giyim = db.Column(db.Float)
    hazir_yemek = db.Column(db.Float)
    saglik = db.Column(db.Float)
    mobilya = db.Column(db.Float)
    egitim = db.Column(db.Float)
    kdiger = db.Column(db.Float)

    @property
    def toplam(self):
        toplam = round((
                self.market + self.araba + self.giyim + self.hazir_yemek + self.saglik +
                self.mobilya + self.egitim + self.kdiger), 2)
        return toplam


class NakitGider(db.Model):
    tarih_id = db.Column(db.Integer, db.ForeignKey('tarih.id'), primary_key=True, nullable=False)
    atm = db.Column(db.Float)
    kira = db.Column(db.Float)
    aidat = db.Column(db.Float)
    yakit = db.Column(db.Float)
    bes = db.Column(db.Float)
    fon_alim = db.Column(db.Float)
    ndiger = db.Column(db.Float)
    aciklama = db.Column(db.String(100))

    @property
    def toplam(self):
        toplam = round((self.atm + self.kira + self.aidat + self.yakit + self.bes + self.fon_alim + self.ndiger), 2)
        return toplam


class TamamlanmisOdemeler(db.Model):
    tarih_id = db.Column(db.Integer, db.ForeignKey('tarih.id'), primary_key=True, nullable=False)
    ogrenim_kredisi = db.Column(db.Float)
    eminevim = db.Column(db.Float)

    @property
    def toplam(self):
        toplam = round((self.ogrenim_kredisi + self.eminevim), 2)
        return toplam


class Tarih(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    yil = db.Column(db.Integer, nullable=False)
    ay = db.Column(db.Integer, nullable=False)
    gelirler = db.relationship('Gelir', backref='tarih')
    faturalar = db.relationship('Fatura', backref='tarih')
    kredi_karti = db.relationship('KrediKarti', backref='tarih')
    nakit_gider = db.relationship('NakitGider', backref='tarih')
    tamamlanmis_gider = db.relationship('TamamlanmisOdemeler', backref='tarih')


class Diziler(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    isim = db.Column(db.String(100), nullable=False)
    tur = db.Column(db.String(60))
    cikis_tarihi = db.Column(db.Integer, nullable=False)
    son_izlenen = db.Column(db.String(20))
    imdb_puani = db.Column(db.Float)
    imdb_link = db.Column(db.String(100))
    mehmet_puan = db.Column(db.Float)
    ddurum = db.Column(db.String(20), nullable=False)


class Filmler(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    isim = db.Column(db.String(100), nullable=False)
    tur = db.Column(db.String(60))
    cikis_tarihi = db.Column(db.Integer)
    yonetmen = db.Column(db.String(60))
    imdb_puani = db.Column(db.Float)
    imdb_link = db.Column(db.String(100))
    mehmet_puan = db.Column(db.Float)


class Kitaplar(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    isbn = db.Column(db.String(20))
    isim = db.Column(db.String(100), nullable=False)
    tur = db.Column(db.String(200))
    yazar = db.Column(db.String(50))
    yayin_bilgisi = db.Column(db.String(100))
    alinma_yeri = db.Column(db.String(25))
    alinma_tarihi = db.Column(db.Date)
    okunma_durumu = db.Column(db.String(20))


class Yatirimlar(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    tur = db.Column(db.String(15))
    isim = db.Column(db.String(40), nullable=False)
    kisa = db.Column(db.String(7), nullable=False, unique=True)
    birim = db.Column(db.String(10))
    risk = db.Column(db.String(20))
    resim = db.Column(db.String(250))
    durum = db.Column(db.String(7))
    birim_fiyat = db.Column(db.Float)
    alislar = db.relationship('YatirimAlislar', backref='yatirimlar')
    satislar = db.relationship('YatirimSatislar', backref='yatirimlar')

    @property
    def toplam_miktar(self):
        toplam_alis_miktari = 0
        if self.alislar:
            for alis in self.alislar:
                toplam_alis_miktari += alis.miktar
        toplam_satis_miktari = 0
        if self.satislar:
            for satis in self.satislar:
                toplam_satis_miktari += satis.miktar
        toplam_miktar = toplam_alis_miktari - toplam_satis_miktari
        return round(toplam_miktar, 8)

    @property
    def toplam_tutar(self):
        toplam_alis_tutari = 0
        toplam_satis_tutari = 0
        if self.alislar:
            for alis in self.alislar:
                alis_tutari = alis.miktar * alis.birim_fiyat
                toplam_alis_tutari += alis_tutari
        if self.satislar:
            for satis in self.satislar:
                satis_tutari = satis.miktar * satis.birim_fiyat
                toplam_satis_tutari += satis_tutari
        toplam_tutar = toplam_alis_tutari - toplam_satis_tutari
        return round(toplam_tutar, 4)


class YatirimAlislar(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    yatirim = db.Column(db.String(7), db.ForeignKey('yatirimlar.kisa'), nullable=False)
    tarih = db.Column(db.Date)
    miktar = db.Column(db.Float)
    birim_fiyat = db.Column(db.Float)

    @property
    def toplam_tutar(self):
        return round((self.miktar * self.birim_fiyat), 4)


class YatirimSatislar(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    yatirim = db.Column(db.String(7), db.ForeignKey('yatirimlar.kisa'), nullable=False)
    tarih = db.Column(db.Date)
    miktar = db.Column(db.Float)
    birim_fiyat = db.Column(db.Float)

    @property
    def toplam_tutar(self):
        return round((self.miktar * self.birim_fiyat), 4)


class Notlar(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    konu = db.Column(db.String(25), nullable=False)
    icerik = db.Column(db.String(40))
    tarih = db.Column(db.Date, nullable=False)
    durum = db.Column(db.Integer, nullable=False)


class Notlar2(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    konu = db.Column(db.String(25), nullable=False)
    icerik = db.Column(db.String(40))
    tarih = db.Column(db.Date, nullable=False)
    durum = db.Column(db.Integer, nullable=False)
