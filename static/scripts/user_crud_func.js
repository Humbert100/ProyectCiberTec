function new_div(obj){
    let the = `    <div class="single_row_user" id="${obj.id}">
    <div><a href='#' style="text-decoration-color: black;"><p id="row_user">${obj.id}</p></a></div>
    <div><p id="row_email">${obj.email}</p></div>
    <div><p id="row_name">${obj.name}</p></div>
    <div>
        <select id="row_admin" name="">
            <option value="True">True</option>
            <option value="True">False</option>
        </select>
    </div>
    <div><p for="row_super_admin">${obj.superAdmin}</p></div>
    <div>
        <select name="" id="row_block">
            <option value="${obj.block}">${obj.block}</option>
            <option value="True">True</option>
            <option value="False">False</option>
        </select>
    </div>
    <div><p id="row_verified">${obj.verified}</p></div>
</div>`;

}