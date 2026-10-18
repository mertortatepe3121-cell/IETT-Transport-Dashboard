from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "iett_ulasim_platformu_secret_key"


# =====================================================
# KULLANICI BİLGİLERİ
# =====================================================

kullanici_adi_sabit = "mert"
kullanici_sifresi = "1234"


# =====================================================
# LOGIN KONTROLÜ
# =====================================================

@app.before_request
def login_kontrol():

    izinli_endpointler = [
        "login",
        "sifre_unuttum",
        "static"
    ]

    if request.endpoint in izinli_endpointler:
        return

    if not session.get("logged_in"):
        return redirect(url_for("login"))


# =====================================================
# LOGIN
# =====================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        kullanici_adi = request.form.get("kullanici_adi")
        sifre = request.form.get("sifre")

        if (
            kullanici_adi == kullanici_adi_sabit
            and sifre == kullanici_sifresi
        ):

            session["logged_in"] = True
            session["kullanici_adi"] = kullanici_adi

            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            hata="Kullanıcı adı veya şifreyi hatalı girdiniz."
        )

    return render_template("login.html")


# =====================================================
# ŞİFRE YENİLEME
# =====================================================

@app.route("/sifre-unuttum", methods=["GET", "POST"])
def sifre_unuttum():

    global kullanici_sifresi

    if request.method == "POST":

        kullanici_adi = request.form.get("kullanici_adi")
        yeni_sifre = request.form.get("yeni_sifre")
        yeni_sifre_tekrar = request.form.get("yeni_sifre_tekrar")

        # Kullanıcı adı kontrolü
        if kullanici_adi != kullanici_adi_sabit:

            return render_template(
                "sifre_unuttum.html",
                hata="Kullanıcı adı hatalı."
            )

        # Şifrelerin eşleşme kontrolü
        if yeni_sifre != yeni_sifre_tekrar:

            return render_template(
                "sifre_unuttum.html",
                hata="Yeni şifreler eşleşmiyor."
            )

        # Boş şifre kontrolü
        if not yeni_sifre:

            return render_template(
                "sifre_unuttum.html",
                hata="Yeni şifre boş bırakılamaz."
            )

        # Yeni şifreyi kaydet
        kullanici_sifresi = yeni_sifre

        return render_template(
            "sifre_unuttum.html",
            basarili="Şifreniz başarıyla yenilendi. Yeni şifrenizle giriş yapabilirsiniz."
        )

    return render_template("sifre_unuttum.html")


# =====================================================
# LOGOUT
# =====================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# =====================================================
# DASHBOARD
# =====================================================

@app.route("/")
def dashboard():

    return render_template(
        "dashboard.html",
        active_page="dashboard"
    )


@app.route("/rayli-sistem-seferleri")
def rayli_sistem_seferleri():

    import pandas as pd
    import os

    data_path = os.path.join(
        app.root_path,
        "data"
    )

    rows_per_page = 15

    # =====================================================
    # CSV OKUMA
    # =====================================================

    csv_path = os.path.join(
        data_path,
        "rayli_sistem_sefer_sayilari.csv"
    )

    df = pd.read_csv(
        csv_path,
        encoding="utf-8-sig",
        dtype=str
    )

    df = df.fillna("")

    # =====================================================
    # SAYFALAMA
    # =====================================================

    current_page = request.args.get(
        "page",
        1,
        type=int
    )

    total_records = len(df)

    total_pages = max(
        1,
        (total_records + rows_per_page - 1)
        // rows_per_page
    )

    if current_page < 1:
        current_page = 1

    if current_page > total_pages:
        current_page = total_pages

    start = (current_page - 1) * rows_per_page
    end = start + rows_per_page

    page_df = df.iloc[start:end]

    veriler = page_df.to_dict("records")
    columns = list(df.columns)

        # =====================================================
    # VERİ DÖNEMİ
    # CSV'deki gerçek tarih/yıl bilgisinden hesaplanır
    # =====================================================

    veri_donemi = "Belirtilmemiş"

    # Yıl sütununu bul
    yil_sutunu = None

    for column in df.columns:
        if column.strip().lower() in ["yıl", "yil", "year"]:
            yil_sutunu = column
            break

    if yil_sutunu:

        yillar = pd.to_numeric(
            df[yil_sutunu],
            errors="coerce"
        ).dropna()

        if not yillar.empty:

            min_yil = int(yillar.min())
            max_yil = int(yillar.max())

            if min_yil == max_yil:
                veri_donemi = str(min_yil)
            else:
                veri_donemi = f"{min_yil} – {max_yil}"

    # =====================================================
    # HTML
    # =====================================================

    return render_template(
    "panels/rayli_sistem_seferleri.html",

    active_page="rayli-sistem-seferleri",

    veriler=veriler,
    columns=columns,

    current_page=current_page,
    total_pages=total_pages,
    total_records=total_records,

    veri_donemi=veri_donemi
)


@app.route("/durak-hat")
def durak_hat():

    import pandas as pd
    import os

    csv_path = os.path.join(
        app.root_path,
        "data",
        "durak_hat.csv"
    )

    # Sayfa bilgisi
    page = request.args.get("page", 1, type=int)
    rows_per_page = 15

    # CSV'yi oku
    df = pd.read_csv(
        csv_path,
        encoding="utf-8-sig",
        dtype=str
    )

    df = df.fillna("")

    # Sütunları CSV'den direkt al
    columns = list(df.columns)
    print("DURAK HAT SÜTUNLARI:", columns)

    # Toplam kayıt
    total_records = len(df)

    # Toplam sayfa
    total_pages = max(
        1,
        (total_records + rows_per_page - 1) // rows_per_page
    )

    # Geçersiz sayfa kontrolü
    if page < 1:
        page = 1

    if page > total_pages:
        page = total_pages

    # SADECE O SAYFANIN VERİLERİ
    start = (page - 1) * rows_per_page
    end = start + rows_per_page

    page_df = df.iloc[start:end]

    durak_hat_verileri = page_df.to_dict("records")

    return render_template(
    "panels/durak_hat.html",
    active_page="durak",
    durak_hat_verileri=durak_hat_verileri,
    columns=columns,
    current_page=page,
    total_pages=total_pages,
    total_records=total_records,
    veri_donemi="CSV'de belirtilmemiş",
    veri_turu="Durak / Hat"
)

@app.route("/hat-durak-guzergah")
def hat_durak_guzergah():

    import pandas as pd
    import os

    csv_path = os.path.join(
        app.root_path,
        "data",
        "hat_durak_guzergah.csv.csv"
    )

    page = request.args.get("page", 1, type=int)
    rows_per_page = 15

    df = pd.read_csv(
        csv_path,
        encoding="utf-8-sig",
        dtype=str
    )

    df = df.fillna("")

    # CSV'de ne sütun varsa aynen kullan
    columns = list(df.columns)

    total_records = len(df)

    total_pages = max(
        1,
        (total_records + rows_per_page - 1) // rows_per_page
    )

    if page < 1:
        page = 1

    if page > total_pages:
        page = total_pages

    start = (page - 1) * rows_per_page
    end = start + rows_per_page

    page_df = df.iloc[start:end]

    guzergah_verileri = page_df.to_dict("records")

    return render_template(
    "panels/hat_durak_guzergah.html",
    active_page="hat-durak-guzergah",
    guzergah_verileri=guzergah_verileri,
    columns=columns,
    current_page=page,
    total_pages=total_pages,
    total_records=total_records,
    veri_donemi="CSV'de belirtilmemiş",
    veri_turu="Hat-Durak-Güzergâh"
)


@app.route("/planlanan-seferler")
def planlanan_seferler():

    import pandas as pd
    import os

    csv_path = os.path.join(
        app.root_path,
        "data",
        "planlanan_seferler.csv"
    )

    page = request.args.get("page", 1, type=int)
    rows_per_page = 15

    df = pd.read_csv(
        csv_path,
        encoding="utf-8-sig",
        dtype=str
    )

    df = df.fillna("")

    # CSV'deki bütün gerçek sütunları kullan
    columns = list(df.columns)

    total_records = len(df)

    total_pages = max(
        1,
        (total_records + rows_per_page - 1) // rows_per_page
    )

    if page < 1:
        page = 1

    if page > total_pages:
        page = total_pages

    start = (page - 1) * rows_per_page
    end = start + rows_per_page

    page_df = df.iloc[start:end]

    sefer_verileri = page_df.to_dict("records")

    return render_template(
    "panels/planlanan_seferler.html",
    active_page="planlanan",
    sefer_verileri=sefer_verileri,
    columns=columns,
    current_page=page,
    total_pages=total_pages,
    total_records=total_records,
    veri_donemi="CSV'de belirtilmemiş",
    veri_turu="Planlanan Sefer Saati"
)

@app.route("/sefer-gerceklesme")
def sefer_gerceklesme():

    import pandas as pd
    import os

    csv_path = os.path.join(
        app.root_path,
        "data",
        "sefer_gerceklesme_api.csv"
    )

    page = request.args.get("page", 1, type=int)
    rows_per_page = 15

    df = pd.read_csv(
        csv_path,
        encoding="utf-8-sig",
        dtype=str
    )

    df = df.fillna("")

    # CSV'deki bütün gerçek sütunları kullan
    columns = list(df.columns)

    total_records = len(df)

    total_pages = max(
        1,
        (total_records + rows_per_page - 1) // rows_per_page
    )

    if page < 1:
        page = 1

    if page > total_pages:
        page = total_pages

    start = (page - 1) * rows_per_page
    end = start + rows_per_page

    page_df = df.iloc[start:end]

    sefer_verileri = page_df.to_dict("records")

    return render_template(
    "panels/sefer_gerceklesme.html",
    active_page="sefer-gerceklesme",
    sefer_verileri=sefer_verileri,
    columns=columns,
    current_page=page,
    total_pages=total_pages,
    total_records=total_records,
    veri_donemi="Belirtilmemiş",
    veri_turu="Gerçekleşen Sefer Verisi"
)


@app.route("/yolculuk-sefer")
def yolculuk_sefer():

    import pandas as pd
    import os

    csv_path = os.path.join(
        app.root_path,
        "data",
        "yolculuk_sefer_api.csv"
    )

    page = request.args.get("page", 1, type=int)
    rows_per_page = 15

    df = pd.read_csv(
        csv_path,
        encoding="utf-8-sig",
        dtype=str
    )

    df = df.fillna("")

    # CSV'deki gerçek sütunlar
    columns = list(df.columns)

    total_records = len(df)

    total_pages = max(
        1,
        (total_records + rows_per_page - 1) // rows_per_page
    )

    if page < 1:
        page = 1

    if page > total_pages:
        page = total_pages

    start = (page - 1) * rows_per_page
    end = start + rows_per_page

    page_df = df.iloc[start:end]

    yolculuk_verileri = page_df.to_dict("records")

    return render_template(
        "panels/yolculuk_sefer.html",
        active_page="yolculuk",
        yolculuk_verileri=yolculuk_verileri,
        columns=columns,
        current_page=page,
        total_pages=total_pages,
        total_records=total_records,
        veri_donemi=(
            f"{df['Tarih'].iloc[0]} - {df['Tarih'].iloc[-1]}"
            if "Tarih" in df.columns and len(df) > 0
            else "Belirtilmemiş"
        ),
        veri_turu="Yolculuk / Sefer Verisi"
    )

@app.route("/ulasim-talebi")
def ulasim_talebi():

    import pandas as pd
    import os

    rows_per_page = 15

    data_path = os.path.join(
        app.root_path,
        "data"
    )

    # =====================================================
    # CSV DOSYALARI
    # =====================================================

    hat_2020_path = os.path.join(
        data_path,
        "2020_hat_verileri.csv"
    )

    hat_2040_path = os.path.join(
        data_path,
        "2040_hat_verileri.csv"
    )

    comparison_path = os.path.join(
        data_path,
        "2020_2040_hat_karsilastirma.csv"
    )

    road_2020_path = os.path.join(
        data_path,
        "2020_karayolu_agi.csv"
    )

    road_2040_path = os.path.join(
        data_path,
        "2040_karayolu_agi.csv"
    )

    # =====================================================
    # SAYFA NUMARALARI
    # Her tablonun kendi sayfası vardır.
    # =====================================================

    hat_2020_page = request.args.get(
        "hat_2020_page",
        1,
        type=int
    )

    hat_2040_page = request.args.get(
        "hat_2040_page",
        1,
        type=int
    )

    comparison_page = request.args.get(
        "comparison_page",
        1,
        type=int
    )

    road_2020_page = request.args.get(
        "road_2020_page",
        1,
        type=int
    )

    road_2040_page = request.args.get(
        "road_2040_page",
        1,
        type=int
    )

    # =====================================================
    # CSV'LERİ OKU
    # =====================================================

    hat_2020_df = pd.read_csv(
        hat_2020_path,
        encoding="utf-8-sig",
        dtype=str
    )

    hat_2040_df = pd.read_csv(
        hat_2040_path,
        encoding="utf-8-sig",
        dtype=str
    )

    comparison_df = pd.read_csv(
        comparison_path,
        encoding="utf-8-sig",
        dtype=str
    )

    road_2020_df = pd.read_csv(
        road_2020_path,
        encoding="utf-8-sig",
        dtype=str
    )

    road_2040_df = pd.read_csv(
        road_2040_path,
        encoding="utf-8-sig",
        dtype=str
    )

    # =====================================================
    # BOŞ DEĞERLER
    # =====================================================

    hat_2020_df = hat_2020_df.fillna("")
    hat_2040_df = hat_2040_df.fillna("")
    comparison_df = comparison_df.fillna("")
    road_2020_df = road_2020_df.fillna("")
    road_2040_df = road_2040_df.fillna("")

    # =====================================================
    # 2020 HAT
    # =====================================================

    hat_2020_columns = list(
        hat_2020_df.columns
    )

    hat_2020_total_records = len(
        hat_2020_df
    )

    hat_2020_total_pages = max(
        1,
        (
            hat_2020_total_records
            + rows_per_page
            - 1
        ) // rows_per_page
    )

    if hat_2020_page < 1:
        hat_2020_page = 1

    if hat_2020_page > hat_2020_total_pages:
        hat_2020_page = hat_2020_total_pages

    start = (
        hat_2020_page - 1
    ) * rows_per_page

    end = start + rows_per_page

    hat_2020_verileri = (
        hat_2020_df
        .iloc[start:end]
        .to_dict("records")
    )

    # =====================================================
    # 2040 HAT
    # =====================================================

    hat_2040_columns = list(
        hat_2040_df.columns
    )

    hat_2040_total_records = len(
        hat_2040_df
    )

    hat_2040_total_pages = max(
        1,
        (
            hat_2040_total_records
            + rows_per_page
            - 1
        ) // rows_per_page
    )

    if hat_2040_page < 1:
        hat_2040_page = 1

    if hat_2040_page > hat_2040_total_pages:
        hat_2040_page = hat_2040_total_pages

    start = (
        hat_2040_page - 1
    ) * rows_per_page

    end = start + rows_per_page

    hat_2040_verileri = (
        hat_2040_df
        .iloc[start:end]
        .to_dict("records")
    )

    # =====================================================
    # 2020 - 2040 KARŞILAŞTIRMA
    # =====================================================

    comparison_columns = list(
        comparison_df.columns
    )

    comparison_total_records = len(
        comparison_df
    )

    comparison_total_pages = max(
        1,
        (
            comparison_total_records
            + rows_per_page
            - 1
        ) // rows_per_page
    )

    if comparison_page < 1:
        comparison_page = 1

    if comparison_page > comparison_total_pages:
        comparison_page = comparison_total_pages

    start = (
        comparison_page - 1
    ) * rows_per_page

    end = start + rows_per_page

    comparison_verileri = (
        comparison_df
        .iloc[start:end]
        .to_dict("records")
    )

    # =====================================================
    # 2020 KARAYOLU AĞI
    # =====================================================

    road_2020_columns = list(
        road_2020_df.columns
    )

    road_2020_total_records = len(
        road_2020_df
    )

    road_2020_total_pages = max(
        1,
        (
            road_2020_total_records
            + rows_per_page
            - 1
        ) // rows_per_page
    )

    if road_2020_page < 1:
        road_2020_page = 1

    if road_2020_page > road_2020_total_pages:
        road_2020_page = road_2020_total_pages

    start = (
        road_2020_page - 1
    ) * rows_per_page

    end = start + rows_per_page

    road_2020_verileri = (
        road_2020_df
        .iloc[start:end]
        .to_dict("records")
    )

    # =====================================================
    # 2040 KARAYOLU AĞI
    # =====================================================

    road_2040_columns = list(
        road_2040_df.columns
    )

    road_2040_total_records = len(
        road_2040_df
    )

    road_2040_total_pages = max(
        1,
        (
            road_2040_total_records
            + rows_per_page
            - 1
        ) // rows_per_page
    )

    if road_2040_page < 1:
        road_2040_page = 1

    if road_2040_page > road_2040_total_pages:
        road_2040_page = road_2040_total_pages

    start = (
        road_2040_page - 1
    ) * rows_per_page

    end = start + rows_per_page

    road_2040_verileri = (
        road_2040_df
        .iloc[start:end]
        .to_dict("records")
    )

    # =====================================================
    # HTML
    # =====================================================

    return render_template(
        "panels/ulasim_talep.html",

        active_page="ulasim-talebi",

        # 2020 Hat
        hat_2020_verileri=hat_2020_verileri,
        hat_2020_columns=hat_2020_columns,
        hat_2020_page=hat_2020_page,
        hat_2020_total_pages=hat_2020_total_pages,
        hat_2020_total_records=hat_2020_total_records,

        # 2040 Hat
        hat_2040_verileri=hat_2040_verileri,
        hat_2040_columns=hat_2040_columns,
        hat_2040_page=hat_2040_page,
        hat_2040_total_pages=hat_2040_total_pages,
        hat_2040_total_records=hat_2040_total_records,

        # Karşılaştırma
        comparison_verileri=comparison_verileri,
        comparison_columns=comparison_columns,
        comparison_page=comparison_page,
        comparison_total_pages=comparison_total_pages,
        comparison_total_records=comparison_total_records,

        # 2020 Karayolu
        road_2020_verileri=road_2020_verileri,
        road_2020_columns=road_2020_columns,
        road_2020_page=road_2020_page,
        road_2020_total_pages=road_2020_total_pages,
        road_2020_total_records=road_2020_total_records,

        # 2040 Karayolu
        road_2040_verileri=road_2040_verileri,
        road_2040_columns=road_2040_columns,
        road_2040_page=road_2040_page,
        road_2040_total_pages=road_2040_total_pages,
        road_2040_total_records=road_2040_total_records
    )


@app.route("/iett-duyurular")
def iett_duyurular():

    import pandas as pd
    import os

    csv_path = os.path.join(
        app.root_path,
        "data",
        "iett_duyurular.csv"
    )

    page = request.args.get("page", 1, type=int)
    rows_per_page = 15

    df = pd.read_csv(
        csv_path,
        encoding="utf-8-sig",
        dtype=str
    )

    df = df.fillna("")

    # CSV'deki gerçek sütunlar
    columns = list(df.columns)

    total_records = len(df)

    total_pages = max(
        1,
        (total_records + rows_per_page - 1) // rows_per_page
    )

    if page < 1:
        page = 1

    if page > total_pages:
        page = total_pages

    start = (page - 1) * rows_per_page
    end = start + rows_per_page

    page_df = df.iloc[start:end]

    duyuru_verileri = page_df.to_dict("records")

    return render_template(
        "panels/iett_duyurular.html",

        active_page="iett-duyurular",

        duyuru_verileri=duyuru_verileri,

        columns=columns,

        current_page=page,

        total_pages=total_pages,

        total_records=total_records
    )


@app.route("/iett-gtfs")
def iett_gtfs():

    import pandas as pd
    import os

    data_path = os.path.join(
        app.root_path,
        "data"
    )

    rows_per_page = 15

    # =====================================================
    # CSV OKUMA FONKSİYONU
    # =====================================================
    def read_gtfs_csv(filename):

        csv_path = os.path.join(
            data_path,
            filename
        )

        try:
            df = pd.read_csv(
                csv_path,
                sep=";",
                encoding="utf-8-sig",
                dtype=str
            )

        except UnicodeDecodeError:

            df = pd.read_csv(
                csv_path,
                sep=";",
                encoding="cp1254",
                dtype=str
            )

        df = df.fillna("")

        return df
    # =====================================================
    # PAGINATION FONKSİYONU
    # =====================================================

    def paginate_dataframe(df, page):

        columns = list(df.columns)

        total_records = len(df)

        total_pages = max(
            1,
            (total_records + rows_per_page - 1)
            // rows_per_page
        )

        if page < 1:
            page = 1

        if page > total_pages:
            page = total_pages

        start = (page - 1) * rows_per_page
        end = start + rows_per_page

        page_df = df.iloc[start:end]

        return (
            page_df.to_dict("records"),
            columns,
            page,
            total_pages,
            total_records
        )


    # =====================================================
    # SAYFA NUMARALARI
    # =====================================================

    routes_page = request.args.get(
        "routes_page", 1, type=int
    )

    trips_page = request.args.get(
        "trips_page", 1, type=int
    )

    stops_page = request.args.get(
        "stops_page", 1, type=int
    )

    stop_times_page = request.args.get(
        "stop_times_page", 1, type=int
    )

    calendar_page = request.args.get(
        "calendar_page", 1, type=int
    )

    agency_page = request.args.get(
        "agency_page", 1, type=int
    )


    # =====================================================
    # CSV'LERİ OKU
    # =====================================================

    routes_df = pd.read_csv(
        os.path.join(data_path, "routes.csv"),
        sep=";",
        encoding="utf-8-sig",
        dtype=str
    )

    routes_df = routes_df.fillna("")
       

     
    trips_df = read_gtfs_csv("trips.csv")

    stops_df = read_gtfs_csv("stops.csv")

    stop_times_df = read_gtfs_csv("stop_times.csv")

    calendar_df = read_gtfs_csv("calendar.csv")

    agency_df = read_gtfs_csv("agency.csv")


    # =====================================================
    # PAGINATION
    # =====================================================

    (
        routes_verileri,
        routes_columns,
        routes_page,
        routes_total_pages,
        routes_total_records
    ) = paginate_dataframe(
        routes_df,
        routes_page
    )


    (
        trips_verileri,
        trips_columns,
        trips_page,
        trips_total_pages,
        trips_total_records
    ) = paginate_dataframe(
        trips_df,
        trips_page
    )


    (
        stops_verileri,
        stops_columns,
        stops_page,
        stops_total_pages,
        stops_total_records
    ) = paginate_dataframe(
        stops_df,
        stops_page
    )


    (
        stop_times_verileri,
        stop_times_columns,
        stop_times_page,
        stop_times_total_pages,
        stop_times_total_records
    ) = paginate_dataframe(
        stop_times_df,
        stop_times_page
    )


    (
        calendar_verileri,
        calendar_columns,
        calendar_page,
        calendar_total_pages,
        calendar_total_records
    ) = paginate_dataframe(
        calendar_df,
        calendar_page
    )


    (
        agency_verileri,
        agency_columns,
        agency_page,
        agency_total_pages,
        agency_total_records
    ) = paginate_dataframe(
        agency_df,
        agency_page
    )


    # =====================================================
    # HTML
    # =====================================================

    return render_template(
        "panels/iett_gtfs.html",

        active_page="iett-gtfs",

        # Routes
        routes_verileri=routes_verileri,
        routes_columns=routes_columns,
        routes_page=routes_page,
        routes_total_pages=routes_total_pages,
        routes_total_records=routes_total_records,

        # Trips
        trips_verileri=trips_verileri,
        trips_columns=trips_columns,
        trips_page=trips_page,
        trips_total_pages=trips_total_pages,
        trips_total_records=trips_total_records,

        # Stops
        stops_verileri=stops_verileri,
        stops_columns=stops_columns,
        stops_page=stops_page,
        stops_total_pages=stops_total_pages,
        stops_total_records=stops_total_records,

        # Stop Times
        stop_times_verileri=stop_times_verileri,
        stop_times_columns=stop_times_columns,
        stop_times_page=stop_times_page,
        stop_times_total_pages=stop_times_total_pages,
        stop_times_total_records=stop_times_total_records,

        # Calendar
        calendar_verileri=calendar_verileri,
        calendar_columns=calendar_columns,
        calendar_page=calendar_page,
        calendar_total_pages=calendar_total_pages,
        calendar_total_records=calendar_total_records,

        # Agency
        agency_verileri=agency_verileri,
        agency_columns=agency_columns,
        agency_page=agency_page,
        agency_total_pages=agency_total_pages,
        agency_total_records=agency_total_records
    )

if __name__ == "__main__":
    app.run(debug=True)