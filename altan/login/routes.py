from flask import render_template, request, redirect, url_for, flash, session
from altan.extensions import db, login_manager, UserMixin, login_required, login_user, logout_user
from altan.login import giris
from altan.models import Program, Destek
from urllib.parse import urlparse, urljoin

login_manager.login_view = "giris.login"
login_manager.login_message = ""


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@giris.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter(User.username == username).first()
        if not user:
            flash('Kullanıcı adı hatalı', 'danger')
            return render_template("login.html")
        if not user.password == password:
            flash('Şifre Hatalı', 'danger')
            return render_template("login.html")
        login_user(user, remember=True)
        if "next" in session and session["next"]:
            if is_safe_url(session["next"]):
                return redirect(session["next"])
        return redirect(url_for("main.index"))
    session["next"] = request.args.get("next")
    return render_template("login.html")


@giris.route('/logout')
@login_required
def log_out():
    logout_user()
    return redirect(url_for("giris.login"))


@giris.route('/parametreler/')
def parametreler():
    users = User.query.all()
    programlar = Program.query.all()
    program_sayisi = len(programlar)
    destekler = Destek.query.all()
    defaults = dict(users=users, programlar=programlar, destekler=destekler, sayi=program_sayisi)
    return render_template("parametre.html", defaults=defaults)


@giris.route('/parametreler/ekle/kullanici/', methods=["GET", "POST"])
def parametreler_kullanici_ekle():
    if request.method == 'POST':
        username = request.form.get("kullaniciisimekle")
        password = request.form.get("kullanicisifreekle")
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Kullanıcı Veritabanına Eklenmiştir', 'success')
        return redirect(url_for("giris.parametreler"))
    else:
        flash('Veriler Eklenemedi', 'danger')
        return redirect(url_for("giris.parametreler"))


# @giris.route('/parametreler/sil/program/<int:user_id>/')
# def parametreler_kullanici_sil(user_id):
#     user = User.query.filter(User.id == user_id).first()
#     if user.name == "altan":
#         flash('Altan Kullanıcısı is GOD, cant delete', 'success')
#         return redirect(url_for("giris.parametreler"))
#     else:
#         db.session.delete(user)
#         db.session.commit()
#         flash('Seçilen Kullanıcı Veritabanından Silinmiştir', 'success')
#         return redirect(url_for("giris.parametreler"))


@giris.route('/parametreler/ekle/program/<int:sayi>/', methods=["GET", "POST"])
def parametreler_program_ekle(sayi):
    if request.method == 'POST':
        program_ismi = request.form.get("programisimekle")
        new_program = Program(isim=program_ismi, id = sayi+1)
        db.session.add(new_program)
        db.session.commit()
        flash('Program Veritabanına Eklenmiştir', 'success')
        return redirect(url_for("giris.parametreler"))
    else:
        flash('Veriler Eklenemedi', 'danger')
        return redirect(url_for("giris.parametreler"))


@giris.route('/parametreler/guncelle/program/<int:program_id>/', methods=["GET", "POST"])
def parametreler_program_guncelle(program_id):
    program = Program.query.filter(Program.id == program_id).first()
    if request.method == 'POST':
        program_ismi = request.form.get("programguncelle")
        program.isim = program_ismi
        db.session.commit()
        flash('Program Verileriniz Güncellenmiştir', 'primary')
        return redirect(url_for("giris.parametreler"))
    else:
        flash('Veriler Güncellenemedi', 'danger')
        return redirect(url_for("giris.parametreler"))


@giris.route('/parametreler/sil/program/<int:program_id>/')
def parametreler_program_sil(program_id):
    program = Program.query.filter(Program.id == program_id).first()
    db.session.delete(program)
    db.session.commit()
    flash('Seçilen Program Veritabanından Silinmiştir', 'success')
    return redirect(url_for("giris.parametreler"))


@giris.route('/parametreler/ekle/destek/', methods=["GET", "POST"])
def parametreler_destek_ekle():
    if request.method == 'POST':
        destek_ismi = request.form.get("destekisimekle")
        new_destek = Destek(isim=destek_ismi)
        db.session.add(new_destek)
        db.session.commit()
        flash('Destek Veritabanına Eklenmiştir', 'success')
        return redirect(url_for("giris.parametreler"))
    else:
        flash('Veriler Eklenemedi', 'danger')
        return redirect(url_for("giris.parametreler"))


@giris.route('/parametreler/guncelle/destek/<int:destek_id>/', methods=["GET", "POST"])
def parametreler_destek_guncelle(destek_id):
    destek = Destek.query.filter(Destek.id == destek_id).first()
    if request.method == 'POST':
        destek_ismi = request.form.get("destekguncelle")
        destek.isim = destek_ismi
        db.session.commit()
        flash('Destek Verileriniz Güncellenmiştir', 'primary')
        return redirect(url_for("giris.parametreler"))
    else:
        flash('Veriler Güncellenemedi', 'danger')
        return redirect(url_for("giris.parametreler"))


@giris.route('/parametreler/sil/destek/<int:destek_id>/')
def parametreler_destek_sil(destek_id):
    destek = Destek.query.filter(Destek.id == destek_id).first()
    db.session.delete(destek)
    db.session.commit()
    flash('Seçilen Destek Veritabanından Silinmiştir', 'success')
    return redirect(url_for("giris.parametreler"))
