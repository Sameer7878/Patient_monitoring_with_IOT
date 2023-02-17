
console.log('start');
function setCookie(uid,value,exp_days) {
    let d = new Date();
    d.setTime(d.getTime() + (exp_days*24*60*60*1000));
    let expires = "expires=" + d.toGMTString();
    let user = $("#User").val();
    document.cookies = user + "=" + value + ";" + expires + ";path=/";
}

(function ($) {
    "use strict";
    /*==================================================================
    [ Focus input ]*/
    $('.input100').each(function(){
        $(this).on('blur', function(){
            if($(this).val().trim() != "") {
                $(this).addClass('has-val');
            }
            else {
                $(this).removeClass('has-val');
            }
        })    
    })

    /*=============== [ Validate ]  ===============*/
    let input = $('.validate-input .input100');

    $('.validate-form').on('submit',function(event){
        
        $(".loader").css("visibility", "visible");
        
        let check = true;

        for(let i=0; i<input.length; i++) {
            if(validate(input[i]) == false){
                showValidate(input[i]);
                check=false;
            }
        }
        console.log(check)
        let formData = {
            username: $("#User").val(),
            password: $("#pass").val(),
          };
        console.log(formData);
        $.ajax({
                  type: "POST",
                  url: "/VerifyLogin/",
                  data : JSON.stringify(formData),
                  crossDomain: true,
                  dataType: "json",
                  encode: true,
                  headers: {
                    "Content-Type": "application/json"
                  },
                  processData: false,
                }).done(function (data)  {
                    console.log(data)
                    if(data.status){
                        sessionStorage.setItem('user',$("#User").val());
                        sessionStorage.setItem('token',data.token);
                         var user = sessionStorage.getItem('user');
                        var token = sessionStorage.getItem('token');
                        let formData = {
                                user: user,
                                token: token,
                              };
                        console.log(formData)
                       location.href = "/";
                    }else
                        for(let i=0; i<input.length; i++) {
                            showValidate(input[i]);
                            check = false;
                        }
            //console.log(data.patient[0]._id);
            //setCookie("uid", data.patient[0]._id, 1);
          }).fail(function (data) {
              console.log(data)
            for(let i=0; i<input.length; i++) {
                showValidate(input[i]);
                check=false;

            }
          });
      
          event.preventDefault();

        return check;
    });


    $('.validate-form .input100').each(function(){
        $(this).focus(function(){
           hideValidate(this);
        });
    });

    function validate (input) {
        if((!$(input).attr('type') == 'text') || (!$(input).attr('name') == 'password')) {
            return true;
        }
        else {
            if($(input).val().trim() == ''){
                return false;
            }
        }
    }

    function showValidate(input) {
        let thisAlert = $(input).parent();

        $(thisAlert).addClass('alert-validate');
        $(".alert-v").addClass('alert-validate-s');
        $(".loader").css("visibility", "hidden");
    }

    function hideValidate(input) {
        let thisAlert = $(input).parent();

        $(thisAlert).removeClass('alert-validate');
        $(".alert-v").removeClass('alert-validate-s');
    }
    
    /*==================================================================
    [ Show pass ]*/
    let showPass = 0;
    $('.btn-show-pass').on('click', function(){
        if(showPass == 0) {
            $(this).next('input').attr('type','text');
            $(this).find('i').removeClass('zmdi-eye');
            $(this).find('i').addClass('zmdi-eye-off');
            showPass = 1;
        }
        else {
            $(this).next('input').attr('type','password');
            $(this).find('i').addClass('zmdi-eye');
            $(this).find('i').removeClass('zmdi-eye-off');
            showPass = 0;
        }
        
    });


})(jQuery);
