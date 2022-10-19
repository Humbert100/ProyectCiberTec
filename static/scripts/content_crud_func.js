function new_div(obj){
            let users=`<div class="single_row_content" id="${obj.id}">
                        <div><a href='#' style="text-decoration-color: black;"><p id="row_content">${obj.id}</p></a></div>
                        <div><input type="text" id="row_name" value="${obj.name}"></div>
                        <div>
                            <select name="" id="row_type">
                                <option value="${obj.type}">${obj.type}</option>
                                <option value="hardware">hardware</option>
                                <option value="software">software</option>
                                <option value="EF">EF</option>
                            </select>
                        </div>
                        <div><input type="text" id="row_description" value="${obj.description}"></div>
                        <div>
                            <select name="" id="row_available">
                                <option value="${obj.available}">${obj.available}</option>
                                <option value=0>True</option>
                                <option value=1>False</option>
                            </select>
                        </div>
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
        url         :       "/getall/content",
        data        :       JSON.stringify(user_data_request),
        contentType :       "application/json",
        success     :       function(data){
            var jso = JSON.stringify(data);
            var obj = JSON.parse(jso)
            console.log(obj);
            no_objects = Object.keys(obj).length;
            console.log(no_objects);
            for (var i = 0; i < no_objects; i++){
                new_div(obj[`content_${i}`]);
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

    var userid      = $(`#${id_val} #row_content`).text();
    var requestURL  = {"id": userid}
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

    var id          =   $(`#${id_val} #row_content`).text();
    var name        =   $(`#${id_val} #row_name`).text();
    var type        =   $(`#${id_val} #row_type`).val();
    var description =   $(`#${id_val} #row_description`).text();
    var available   =   $(`#${id_val} #row_available`).val();

    var request_data=  {"id":id,
                        "name":name,
                        "admin":type,
                        "superAdmin":description,
                        "tecAssociate":available
    }

    console.log(request_data);

    $.ajax({
        type            :       "POST",
        url             :       "/update/user/data",
        data            :       JSON.stringify(request_data),
        contentType     :       'application/json',
        dataType        :       "json",
        success         :       function(data){
            //console.log(data.admin)
            
            if (data.admin == "Tchange"){
                if(data.block == 1){
                    alert("Nuevo administrador añadido y se realizo cambios")
                }
                else{
                    alert("Nuevo administrador añadido")
                }
            }
            else if(data.admin == "Cchange"){
                if(data.block == 1){
                    alert("Cambios realizados, no puede añadir nuevos administradores")
                }
                else{
                    alert("No puede agregar nuevos administradores")
                }
            }
            else if(data.admin == "Nchange"){
                if(data.block == 1){
                    alert("Cambios realizados")
                }
                else{
                    alert("Ningun cambio realizado")
                }
            }
            
            
        }
    })
}

