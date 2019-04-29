$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#shopcart_id").val(res._id);
        $("#shopcart_userId").val(res.userID);
        if (res.state == active) {
            $("#shopcart_state").val("Active");
        } else {
            $("#shopcart_state").val("Active");
        }
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#shopcart_userId").val("");
        $("#shopcart_state").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Shopcart
    // ****************************************

    $("#create-btn").click(function () {

        var userId = $("#shopcart_userId").val();
        var state = $("#shopcart_state").val() == "Active";

        var data = {
            "userId": userId,
            "state": state
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/carts",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Shopcart
    // ****************************************

    $("#update-btn").click(function () {

        var shopcart_id = $("#shopcart_id").val();
        var userId = $("#shopcart_userId").val();
        var state = $("#shopcart_state").val() == "true";

        var data = {
            "userId": userId,
            "state": state
        };

        var ajax = $.ajax({
                type: "PUT",
                url: "/carts/" + shopcart_id,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Shopcart
    // ****************************************

    $("#retrieve-btn").click(function () {

        var shopcart_id = $("#shopcart_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/carts/" + shopcart_id,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Shopcart
    // ****************************************

    $("#delete-btn").click(function () {

        var shopcart_id = $("#shopcart_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/carts/" + shopcart_id,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Shopcart has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#shopcart_id").val("");
        clear_form_data()
    });

    // ****************************************
    // Search for a Pet
    // ****************************************

    $("#search-btn").click(function () {

        var userId = $("#shopcart_userId").val();
        var state = $("#shopcart_state").val() == "true";

        var queryString = ""

        if (userId) {
            queryString += 'userId=' + userId
        }
        if (state) {
            if (queryString.length > 0) {
                queryString += '&state=' + state
            } else {
                queryString += 'state=' + state
            }
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/carts?" + queryString,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped" cellpadding="10">');
            var header = '<tr>'
            header += '<th style="width:10%">ID</th>'
            header += '<th style="width:40%">User ID</th>'
            header += '<th style="width:10%">State</th></tr>'
            $("#search_results").append(header);
            var firstshopcart = "";
            for(var i = 0; i < res.length; i++) {
                var shopcart = res[i];
                var row = "<tr><td>"+shopcart._id+"</td><td>"+shopcart.userId+"</td><td>"+shopcart.state+"</td></tr>";
                $("#search_results").append(row);
                if (i == 0) {
                    firstshopcart = shopcart;
                }
            }

            $("#search_results").append('</table>');

            // copy the first result to the form
            if (firstshopcart != "") {
                update_form_data(firstshopcart)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
