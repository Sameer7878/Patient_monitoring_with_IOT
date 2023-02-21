function insert_recent_patient_row(id,patient_name, patient_age, patient_gender,patient_status,as_sta){
    let name=document.getElementById('patient-name');
    let age=document.getElementById('patient-age');
    let gender=document.getElementById('patient-gender');
    let mon_status=document.getElementById('patient-mon-status');
    let assign_staff=document.getElementById('assigned-staff');
    let report=document.getElementById('patient-report');
    name.innerHTML+=`<li id="${id}"><a href="#">${patient_name}</a></li>`;
    age.innerHTML+=`<li id="${id}"><a href="#">${patient_name}</a></li>`;
    gender.innerHTML+=`<li id="${id}"><a href="#">${patient_gender}</a></li>`;
    mon_status.innerHTML+=`<li id="${id}"><a href="#">${patient_status}</a></li>`;
    assign_staff.innerHTML+=`<li id="${id}"><a href="#">${as_sta}</a></li>`;
    report.innerHTML+=`<li><a href="#"><u>View</u></a></li>`;
}
function insert_patient_row(id,patient_name, patient_age, patient_gender,patient_status,as_sta){
    let name=document.getElementById('patient-name2');
    let age=document.getElementById('patient-age2');
    let gender=document.getElementById('patient-gender2');
    let mon_status=document.getElementById('patient-mon-status2');
    let assign_staff=document.getElementById('assigned-staff2');
    let report=document.getElementById('patient-report2');
    name.innerHTML+=`<li id="${id}"><a href="#">${patient_name}</a></li>`;
    age.innerHTML+=`<li id="${id}"><a href="#">${patient_name}</a></li>`;
    gender.innerHTML+=`<li id="${id}"><a href="#">${patient_gender}</a></li>`;
    mon_status.innerHTML+=`<li id="${id}"><a href="#">${patient_status}</a></li>`;
    assign_staff.innerHTML+=`<li id="${id}"><a href="#">${as_sta}</a></li>`;
    report.innerHTML+=`<li><a id="${id}" onclick="showdetails(this.id);" style="cursor: pointer;"><u>View</u></a></li>`;
}
let ws;
 var GetCheck=true
function UpdateDataByID(data){
       newArray1 = newArray1.concat(parseInt(data.data.pulse_oxi.pulse))
        newArray1.splice(0, 1)
        newArray3 = newArray3.concat(parseInt(data.data.pulse_oxi.spo2))
        newArray3.splice(0, 1)
    $('.heartrate').text(data.data.pulse_oxi.pulse);
    $('.spo2').text(data.data.pulse_oxi.spo2);
    $('.oxy-pres').text(data.data.oxy_pres.percentage);
    $('.saline-per').text(data.data.saline_per.percentage);
      var data_update1 = {
    y: [newArray1]
    };
    var data_update3 = {
    y: [newArray3]
    };
      Plotly.update('ecg-graph', data_update1);
      Plotly.update('spo2-graph', data_update3);

}
var user = sessionStorage.getItem('user');
var token = sessionStorage.getItem('token');
(function ($) {
    "use strict";

    $(".log_out").click(function () {
        sessionStorage.removeItem('token');
        location.href = "/login/"
    });

    $(".check-sensor").click(function (){
        $.ajax({
        type: "GET",
        url: "/CheckSensor/"+this.id+"/",
        crossDomain: true,
        dataType: "json",
        encode: true,
      }).done(function (data) {
            if(data.state){
                console.log('dstat')
                var classname='res_check'+data.id;
                console.log(classname)
                document.getElementsByClassName(classname)[0].style.color='green';
                document.getElementsByClassName(classname)[0].innerText="Active";
            }
        });
    });



    if (token == null) {
        location.href = "/login/"
        return 0;
    }
    console.log(token)
    $.ajax({
        type: "GET",
        url: "/GetRecentPatientData/"+token+"/",
        crossDomain: true,
        dataType: "json",
        encode: true,
      }).done(function (data) {
          console.log(data)
          for(var id in data){
              insert_recent_patient_row(data[id].patient_id,data[id].name,data[id].age,data[id].gender,data[id].mon_stat,data[id].assigned);
          }


    });
    $.ajax({
        type: "GET",
        url: "/GetAllPatientData/"+token+"/",
        crossDomain: true,
        dataType: "json",
        encode: true,
      }).done(function (data) {
          console.log(data)
          for(var id in data){
              insert_patient_row(data[id].id,data[id].name,data[id].age,data[id].gender,data[id].mon_stat,data[id].assigned);
          }


    });
    $.ajax({
        type: "GET",
        url: "/GetHospitalData/"+token+"/",
        crossDomain: true,
        dataType: "json",
        encode: true,
      }).done(function (data) {
          console.log(data)
            $('.total_checkups').text(data.TotalCheckups);
            $('.total_patients').text(data.TotalPatients);
            $('.total_staff').text(data.TotalStaff);
            $('.active_beds').text(data.ActiveBeds);
            preLoaderHandler();
    });
      /*$.ajax({
        type: "GET",
        url: "https://healthconnect-server.onrender.com/geo_locate/"+user,
        dataType: "json",
        encode: true,
      }).done(function (data) {
        
        $.ajax({
          type: "GET",
          url: "https://api.ipgeolocation.io/ipgeo?apiKey=" + data.geo_api,
          dataType: "json",
          encode: true,
        }).done(function (data) {
          console.log(data.city);
          sessionStorage.setItem('geo_loc',data.city);
          
        }).fail(function (data) {
          console.log("api failed");
        });
        
      }).fail(function (data) {
        console.log("geo server failed");
      });

      var map_link = "https://maps.google.com/maps?q=hospitals%20in%20"+sessionStorage.getItem('geo_loc')+"&t=&z=10&ie=UTF8&iwloc=&output=embed";
      $('#hospital-map').attr('src', map_link);*/

    const protocol = window.location.protocol.includes('https') ? 'wss' : 'ws';
    ws = new WebSocket(`${protocol}://${location.host}/EstablishConn/${token}`);
    ws.onmessage = function (event) {
        //var douquot=event.data.replace(/'/g, '"');
        var patient_data = JSON.parse(event.data);
        console.log(patient_data)
        UpdateDataByID(patient_data);
        preLoaderHandler();
        if(GetCheck){
            ws.send(JSON.stringify({"status": "active", "id": patient_data.data.patient_id}))
        }
    }

})(jQuery);




$('.key-setting').hide();
$('.dev-create').hide();
$('.pop-up').hide();

function view_key_modal(){
  $('.key-setting').show();
  $('.pop-up').show();  
  $('#blur').css('filter', 'blur(5px)');   
}

function view_node_modal(){
  $('.dev-create').show();
  $('.pop-up').show();  
  $('#blur').css('filter', 'blur(5px)');   
}

function close_key(){
  $('.key-setting').hide();
  $('.dev-create').hide();
  $('.pop-up').hide();   
  $('#blur').css('filter', 'blur(0px)');   
}

function copyToClipboard(element) {
  var $temp = $("<input>");
  $("body").append($temp);
  $temp.val($(element).html()).select();
  document.execCommand("copy");
  $temp.remove();
 }

 function gen_newkey(){
  
  let url = "https://healthconnect-server.onrender.com/devtkn/create?user="+sessionStorage.getItem('user')+"&pass="+$('input.key-pass').val();
  
  $.ajax({
    type: "GET",
    url: url,
    crossDomain: true,
    dataType: "json",
    encode: true,
    headers: {
      "Content-Type": "application/json"
    },
    processData: false,
  }).done(function (data) {
    $('.key-setting .key-value').text(data.device_token);
    $('input.key-pass').val('');
    //console.log("Updated");
  }).fail(function (data) {
    console.log("update failed");
    
  });

 }

 function showdetails(id){
    GetCheck=true
    console.log(id)
    $('.diagnosis.dashboard').removeClass('active');
    $('.overview.dashboard').addClass('active');
    ws.send(JSON.stringify({"status": "active", "id": parseInt(id)}));
 }

  function BackToList(){
    $('.diagnosis.dashboard').addClass('active');
    $('.overview.dashboard').removeClass('active');
    GetCheck=false
 }

var arrayLength = 60
var newArray1 = []
var newArray3 = []
var newArray4 = []

for(var i = 0; i < arrayLength; i++) {
  newArray1[i] = 0
  newArray3[i] = 0
  newArray4[i] = 0
}

Plotly.plot('ecg-graph', [{
  y: newArray1,
  mode: 'lines',
  line: {
    color: '#80CAF6',
    shape: 'spline'
  }
}]);

Plotly.plot('spo2-graph', [{
  y: newArray3,
  mode: 'lines',
  line: {
    color: '#bf80f6',
    shape: 'spline'
  }
}]);

