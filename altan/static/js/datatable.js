$.extend($.fn.dataTable.defaults, {
    dom:
      "<'row'<'col-md-12'tr>>" + "<'row'<'col-md-4'l><'col-md-4'i><'col-md-4'p>>",
    language: {
      url: "https://cdn.datatables.net/plug-ins/1.10.22/i18n/Turkish.json",
    },
  
    pageLength: 10,
    lengthMenu: [
      [10, 25, 50, -1],
      [10, 25, 50, "All"],
    ],
    
    "bDestroy": true
  });
  
  $(function () {
    $("#projeler").DataTable({
      columnDefs: [
        { width: "2%", targets: 0 },
        { width: "24%", targets: 1 },
        { width: "8%", targets: 2 },
        { width: "20%", targets: 3 },
        { width: "8%", targets: 4 },
        { width: "4%", targets: 5 },
        { width: "8%", targets: 6 },
        { width: "8%", targets: 7 },
        { width: "4%", targets: 8 },
        { width: "4%", targets: 9 },
      ],
    });
  
    $("#projeler_ara").on("input", function (e) {
      e.preventDefault();
      $("#projeler").DataTable().search($(this).val()).draw();
    });
  });
  
  $(function () {
    $("#odemeler").DataTable({
      columnDefs: [
        { width: "30%", targets: 1 },
        { width: "20%", targets: 3 },
        { width: "10%", targets: 6 },
      ],
    });
  
    $("#odemeler_ara").on("input", function (e) {
      e.preventDefault();
      $("#odemeler").DataTable().search($(this).val()).draw();
    });
  });
  
  $(function () {
    $("#isletmeler").DataTable({});
  
    $("#isletmeler_ara").on("input", function (e) {
      e.preventDefault();
      $("#isletmeler").DataTable().search($(this).val()).draw();
    });
  });
  
  $(function () {
    $("#kitaplar").DataTable({
      columnDefs: [
        { width: "2%", targets: 0 },
        { width: "20%", targets: 1 },
        { width: "16%", targets: 2 },
        { width: "13%", targets: 3 },
        { width: "20%", targets: 4 },
        { width: "5%", targets: 5 },
        { width: "10%", targets: 6 },
        { width: "7%", targets: 7 },
        { width: "7%", targets: 8 },
      ],
    });
  
    $("#kitap_ara").on("input", function (e) {
      e.preventDefault();
      $("#kitaplar").DataTable().search($(this).val()).draw();
    });
  });
  
  $(function () {
    $("#diziler").DataTable({
      columnDefs: [
        { width: "20%", targets: 1 },
        { width: "10%", targets: 2 },
        { width: "20%", targets: 3 },
      ],
    });
  
    $("#dizi_ara").on("input", function (e) {
      e.preventDefault();
      $("#diziler").DataTable().search($(this).val()).draw();
    });
  });
  
  $(function () {
    $("#filmler").DataTable({});
  
    $("#film_ara").on("input", function (e) {
      e.preventDefault();
      $("#filmler").DataTable().search($(this).val()).draw();
    });
  });