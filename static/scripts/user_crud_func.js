function new_div(obj){
            let users=`<div class="single_row_user" id="${obj.id}">
                        <div><a href='#' style="text-decoration-color: black;"><p id="row_user">${obj.id}</p></a></div>
                        <div><p id="row_email">${obj.email}</p></div>
                        <div><p id="row_name">${obj.name}</p></div>
                        <div>
                            <select id="row_admin" name="">
                                <option value="${obj.admin}">${obj.admin}</option>
                                <option value="True">True</option>
                                <option value="False">False</option>
                            </select>
                        </div>
                        <div><p for="row_super_admin">${obj.superAdmin}</p></div>
                        <div><p for="row_tecAssociate">${obj.tecAssociate}</p></div>
                        <div>
                            <select name="" id="row_block">
                                <option value="${obj.block}">${obj.block}</option>
                                <option value="True">True</option>
                                <option value="False">False</option>
                            </select>
                        </div>
                        <div><p id="row_verified">${obj.verified}</p></div>
                        <div><button id="row_save" onclick="save_button('${obj.id}');">save</button></div>
                        <div><button id="row_delete" onclick="delete_button('${obj.id}');">delete</button></div>
                    </div>`;
        $('.div_list_users').append(users);
        console.log("Works")
    
}

function add_div(){
    var user_data_request = {"nothing": "to see"}

    $.ajax({
        type        :       "POST",
        url         :       "/getall/users",
        data        :       JSON.stringify(user_data_request),
        contentType :       "application/json",
        success     :       function(data){
            var jso = JSON.stringify(data);
            var obj = JSON.parse(jso)
            console.log(obj);
            no_objects = Object.keys(obj).length;
            console.log(no_objects);
            for (var i = 0; i < no_objects; i++){
                new_div(obj[`user_${i}`]);
            }
        }
    });
}

window.onload = add_div();

function move_rows(id_val){
    $(`#${id_val}`).remove();
}

function delete_button(id_val){
    anime({
        targets:        `#${id_val}`,
        translatex:     1500,
        easing:         "easeInOutCubic"
    });
    setTimeout(move_rows, 800, id_val);

    var userid      = $(`#${id_val} #row_user`).text();
    var requestURL  = {"userId": userid}
    //console.log(userid)
    console.log(requestURL)

    
    $.ajax({
        type            : "POST",
        url             : "/delete/user",
        data            : JSON.stringify(requestURL),
        contentType     : 'application/json',
        dataType        : 'json',

        success         : function(data){
            var jso     = JSON.stringify(data);
            var obj     = JSON.parse(jso);
            console.log(obj);
            alert("Usuario eliminado exitosamente")
        }
    });          
}

function save_button(id_val){

    var id          =   $(`#${id_val} #row_user`).text();
    var email       =   $(`#${id_val} #row_email`).text();
    var name        =   $(`#${id_val} #row_name`).text();
    var admin       =   $(`#${id_val} #row_admin`).text();
    var superAdmin  =   $(`#${id_val} #row_superAdmin`).text();
    var tecAssociate=   $(`#${id_val} #row_tecAssociate`).text();
    var block       =   $(`#${id_val} #row_block`).text();
    var verified    =   $(`#${id_val} #row_verified`).text();

    var request_data=  {"id":id,
                        "email":email,
                        "name":name,
                        "admin":admin,
                        "superAdmin":superAdmin,
                        "tecAssociate":tecAssociate,
                        "block":block,
                        "verified":verified
    }

    console.log(request_data);

    $.ajax({
        type            :       "POST",
        url             :       ""
    })
}

