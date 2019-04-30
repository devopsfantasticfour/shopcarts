$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the shopcart form with data from the response
    function update_form_data(res) {
        $("#shopcart_id").val(res._id);
        $("#shopcart_userId").val(res.userID);
        if (res.state == active) {
            $("#shopcart_state").val("Active");
        } else {
            $("#shopcart_state").val("Active");
        }
    }

    /// Clears all shopcart form fields
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
    // Search for a ShopCart
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

    // ****************************************
    // Shopcart Items
    // ****************************************


    // Updates the shopcart item form with data from the response
    function update_form_data_item(res_item) {
        $("#cartId").val(res_item._id);
        $("#item_id").val(res_item.item_id);
        $("#item_price").val(res_item.item_price);
        $("#item_productID").val(res_item.item_productID);
        $("#item_quantity").val(res_item.item_quantity);
    }

    /// Clears all shopcart item form fields
    function clear_form_data_item() {
        $("#cartId").val("");
        $("#item_id").val("");
        $("#item_price").val("");
        $("#item_productID").val("");
        $("#item_quantity").val("");
    }


    // ****************************************
    // Create an Item
    // ****************************************

    $("#create-item-btn").click(function () {

        var item_cartId = $("#item_cartId").val();
        var item_price = $("#item_price").val();
        var item_productID = $("#item_productID").val();
        var item_quantity = $("#item_quantity").val();

        var data = {
            "item_cartId": cartId,
            "price": item_price,
            "productID": item_productID,
            "quantity": item_quantity
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/carts" + item_cartId + "/items",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res_item){
            update_form_data(res_item)
            flash_message("Success")
        });

        ajax.fail(function(res_item){
            flash_message(res_item.responseJSON.message)
        });
    });

    // ****************************************
    // Update an Item
    // ****************************************

    $("#update-item-btn").click(function () {

      var item_cartId = $("#item_cartId").val();
      var item_id = $("#item_id").val();
      var item_price = $("#item_price").val();
      var item_productID = $("#item_productID").val();
      var item_quantity = $("#item_quantity").val();

        var data = {
          "item_cartId": item_cartId,
          "price": item_price,
          "productID": item_productID,
          "quantity": item_quantity
        };

        var ajax = $.ajax({
                type: "PUT",
                url: "/carts/" + item_cartId + "/items/" + item_id,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res_item){
            update_form_data(res_item)
            flash_message("Success")
        });

        ajax.fail(function(res_item){
            flash_message(res_item.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Shopcart Item
    // ****************************************

    $("#retrieve-item-btn").click(function () {

        var cartId = $("#cartId").val();
        var item_id = $("#item_id").val();

        var ajax_item = $.ajax({
            type: "GET",
            url: "/carts/" + cartId + "/items/" + item_id,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res_item){
            //alert(res.toSource())
            update_form_data_item(res_item)
            flash_message("Success")
        });

        ajax.fail(function(res_item){
            clear_form_data_item()
            flash_message(res_item.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Shopcart Item
    // ****************************************

    $("#delete-item-btn").click(function () {

        var cartId = $("#cartId").val();
        var item_id = $("#item_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/carts/" + cartId + "/items/" + item_id,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res_item){
            clear_form_data_item()
            flash_message("Shopcart Item has been Deleted!")
        });

        ajax.fail(function(res_item){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-item-btn").click(function () {
        $("#cartId").val("");
        $("#item_id").val("");
        $("#item_cartId").val("");
        $("#item_price").val("");
        $("#item_productID").val("");
        $("#item_quantity").val("");
        clear_form_data()
    });


    // ****************************************
    // Search for an Item
    // ****************************************

    $("#search-item-btn").click(function () {

        var item_cartId = $("#item_cartId").val();
        var item_price = $("#item_price").val();
        var item_productID = $("#item_productID").val();
        var item_quantity = $("#item_quantity").val();

        var queryString = ""

        if (item_price) {
            queryString += 'item_price=' + item_price
        }
        if (item_productID) {
            if (queryString.length > 0) {
                queryString += '&item_productID=' + item_productID
            } else {
                queryString += 'item_productID=' + item_productID
            }
        }
        if (item_quantity) {
            if (queryString.length > 0) {
                queryString += '&item_quantity=' + item_quantity
            } else {
                queryString += 'item_quantity=' + item_quantity
            }
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/carts/" + item_cartId + "/items?" + queryString,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_items_results").empty();
            $("#search_items_results").append('<table class="table-striped" cellpadding="10">');
            var header = '<tr>'
            header += '<th style="width:10%">Cart ID</th>'
            header += '<th style="width:40%">Item ID</th>'
            header += '<th style="width:10%">Price</th>'
            header += '<th style="width:10%">Product ID</th>'
            header += '<th style="width:10%">Quantity</th>
            </tr>'
            $("#search_items_results").append(header);
            var firstitem = "";
            for(var i = 0; i < res.length; i++) {
                var item = res[i];
                var row = "<tr><td>"+item.cartId+"</td><td>"+item._id+"</td><td>"+item.price+"</td><td>"+item.productId+"</td><td>"+item.quantity+"</td></tr>";
                $("#search_items_results").append(row);
                if (i == 0) {
                    firstitem = item;
                }
            }

            $("#search_items_results").append('</table>');

            // copy the first result to the form
            if (firstitem != "") {
                update_form_data(firstitem)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });


})
