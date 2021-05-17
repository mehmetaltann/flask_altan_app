$(function () {
  var toplam_degerler = $(".nemesis");
  var butun_deger = 0;
  var getiriler = $(".afrodit");
  var toplam_getiri = 0;
  var getirs = [];
  var degers = [];

  $.each(toplam_degerler, function (_index, value) {
    degers.push(
      $(value)
        .text()
        .replace("Değer : ", "")
        .replace(" TL", "")
        .replace(",", "")
        .replace(",", "")
    );
  });

  for (var i = 0; i < degers.length; i++) {
    butun_deger += parseFloat(degers[i]);
  }

  $.each(getiriler, function (_index, value) {
    getirs.push(
      $(value)
        .text()
        .replace("Getiri : ", "")
        .replace(" TL", "")
        .replace(",", "")
        .replace(",", "")
    );
  });

  for (var i = 0; i < getirs.length; i++) {
    toplam_getiri += parseFloat(getirs[i]);
  };

  $("input[name='toplamyatirim']").val(butun_deger);

  $("input[name='toplamgetiri']").val(toplam_getiri);

});
