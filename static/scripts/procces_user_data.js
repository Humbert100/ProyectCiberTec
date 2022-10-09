function process_login_info(){
    var continue_next = true;
    
    switch(true){
        case(!("#user_email").val()):
            alert("Favor de ingresar su correo");
            continue_next = false;
        break;
        case(!("#user_pwd").val()):
            alert("Favor de ingresar su contraseña");
            continue_next = false;
        break;
    }
    if(continue_next == false){
        console.log("not registered");
        return;
    }

    let user_login_data = {'email'  :   $("user_email").val(),
                           'pwd'    :   $("user_pwd").val()};
    console.log(user_login_data)

    $.ajax({
        type        :   "POST",
        url         :   "/user/login",
        data        :   JSON.stringify(user_login_data),
        contentType :   'application/json',
        dataType    :   "json",

        success: function (data){
            if (data.authorized == true)    {
                location.replace("/homepage");
            }
            else if(data.authorized == "exist"){
                alert("EL usuario no existe, favor de registrarse");
            }
            else if(data.authorized == "available"){
                alert("EL usuario no verificado, favor de consultar su correo");
            }
            else if(data.authorized == "pwd"){
                alert("contraseña incorrecta, favor de volver a colocarla");
            }
        }
    })

}

function process_sign_in_info(){
    var continue_next = true;
    
    switch(true){
        case(!("#user_name").val()):
            alert("Favor de ingresar su nombre");
            continue_next = false;
        break;
        case(!("#user_lastname").val()):
            alert("Favor de ingresar su o sus apellidos");
            continue_next = false;
        break;
        case(!("#user_email").val()):
            alert("Favor de ingresar su correo");
            continue_next = false;
        break;
        case(!("#user_pwd").val()):
            alert("Favor de ingresar su contraseña");
            continue_next = false;
        break;
        case(!("#user_pwd_confirmation").val()):
            alert("Favor de ingresar su contraseña");
            continue_next = false;
        break;
        case(("#user_pwd_confirmation").val() != ("#user_pwd").val()):
            alert("Las contraseñas no coinciden, favor de verificar");
            continue_next = false;
        break;
        case(document.getElementById("checkbox").value == false):
            alert("Porfavor, acepta los terminos y condiciones")
            continue_next = false
        break;
    }
    if(continue_next == false){
        console.log("usuario invalido para registrar");
        return;
    }

    let name = ("#user_name").val() + " " + ("#user_lastname").val()
    let user_sign_up_data = {   'name'      :   name,
                                'email'     :   $("user_email").val(),
                                'pwd'       :   $("user_pwd").val()};
    console.log(user_sign_up_data)

    $.ajax({
        type        :   "POST",
        url         :   "/user/create",
        data        :   JSON.stringify(user_login_data),
        contentType :   'application/json',
        dataType    :   "json",
    
        success: function (data)    {
            if (data.register == True){
                alert("usuario registrado")
            }
            if (data.register == "Exist"){
                alert("Correo ya registrado, favor de probar con otro")
            }
        }

    })
}