$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#product_id").val(res.product_id);
        $("#user_id").val(res.user_id);
        $("#quantity").val(res.quantity);
        $("#price").val((res.price).toFixed(2)); //Rounding to 2 decimal places so that we can compare value of price in scenarios
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#product_id").val("");
        $("#user_id").val("");
        $("#quantity").val("");
        $("#price").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Add Item to Shopcart
    // ****************************************

    $("#create-btn").click(function () {

        var product_id = $("#product_id").val();
        var user_id = $("#user_id").val();
        var quantity = $("#quantity").val();
        var price = $("#price").val();

        var data = {
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity,
            "price": price

        };

        var ajax = $.ajax({
            type: "POST",
            url: "/shopcarts",
            contentType:"application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            $("#search_results").empty();
            $("#query_search_results").empty();
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            $("#search_results").empty();
            $("#query_search_results").empty();
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update an item in shopcart
    // ****************************************

    $("#update-btn").click(function () {

        var product_id = $("#product_id").val();
        var user_id = $("#user_id").val();
        var quantity = $("#quantity").val();
        var price = $("#price").val();

        var data = {
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity,
            "price": price

        };

        var ajax = $.ajax({
                  type: "PUT",
                  url: "/shopcarts/"+user_id+"/product/"+product_id,
                  contentType:"application/json",
                  data: JSON.stringify(data)
        })

        ajax.done(function(res){
            $("#search_results").empty();
            $("#query_search_results").empty();
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            $("#search_results").empty();
            $("#query_search_results").empty();
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve an item in shopcart
    // ****************************************

    $("#retrieve-btn").click(function () {

        var product_id = $("#product_id").val();
        var user_id = $("#user_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/shopcarts/"+user_id+"/product/"+product_id,
            contentType:"application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            $("#query_search_results").empty();
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            $("#search_results").empty();
            $("#query_search_results").empty();
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });



    // ****************************************
    // Retrieve All items in shopcart
    // ****************************************

    $("#retrieve-all-btn").click(function () {
        var user_id = $("#user_id").val();

	if (user_id == '') {
            var ajax = $.ajax({
                type: "GET",
                url: "/shopcarts",
                contentType:"application/json",
                data: ''
            })
	    ajax.done(function(res){
		var header = "";
                $("#search_results").empty();
                $("#query_search_results").empty();
                $("#search_results").append('<table class="table-striped">');

		var obj = jQuery.parseJSON(res);
                for (var i=0;i<obj.length;i++) {
		    usr_id = obj[i].user_id;
		    header = '<tr><colspan=3><td><b>User ID</b> : '+usr_id+"</td></tr>";
		    $("#search_results").append(header);
                    prod = obj[i].products;
		    header = "<tr><td width=45%>Product ID</td><td width=30%>Price</td><td>Quantity</td></tr>";
		    for (var j=0;j<prod.length;j++) {
                        prod_id = prod[j].product_id;
			price = prod[j].price;
			quantity = prod[j].quantity;
			header += "<tr><td>"+prod_id+"</td><td>"+price+"</td><td>"+quantity+"</td></tr>";


                    }
		    header += "<tr><td colspan=3>&nbsp;</td><tr>";
		    $("#search_results").append(header);

		}

		$("search_results").append("</table>");
                flash_message("Success")
            });
            ajax.fail(function(res){
                $("#search_results").empty();
                $("#query_search_results").empty();
                clear_form_data()
                flash_message(res.responseJSON.message)
            });





	} else {


            var ajax = $.ajax({
                type: "GET",
                url: "/shopcarts/"+user_id,
                contentType:"application/json",
                data: ''
            })

            ajax.done(function(res){
                //alert(res.toSource())
                $("#search_results").empty();
                $("#query_search_results").empty();
                $("#search_results").append('<table class="table-striped"><thead>');
                var header = '<tr>'
                header += '<th style="width:35%">Product</th>'
                header += '<th style="width:45%">Quantity</th>'
                header += '<th style="width:20%">Price</th></tr>'
                $("#search_results").append(header);
                for(var i = 0; i < res.length; i++) {
                    product = res[i];
                    var row = "<tr><td>"+product.product_id+"</td><td>"+product.quantity+"</td><td>"+product.price+"</td></tr>";
                    $("#search_results").append(row);
                }

                $("#search_results").append('</thead></table>');

                flash_message("Success")
            });

            ajax.fail(function(res){
                $("#search_results").empty();
                $("#query_search_results").empty();
                clear_form_data()
                flash_message(res.responseJSON.message)
            });
	}

    });

    // ****************************************
    // Delete a Product in Shopcart
    // ****************************************

    $("#delete-btn").click(function () {

        var product_id = $("#product_id").val();
        var user_id = $("#user_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/shopcarts/"+user_id+"/product/"+product_id,
            contentType:"application/json",
            data: '',
        })

        ajax.done(function(res){
            $("#search_results").empty();
            $("#query_search_results").empty();
            clear_form_data()
            flash_message("Product with ID [" + res.id + "] has been Deleted from User having ID [" + res.user_id + "]!")
        });

        ajax.fail(function(res){
            $("#search_results").empty();
            $("#query_search_results").empty();
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Delete All Products in Shopcart
    // ****************************************

    $("#delete-all-btn").click(function () {

        var user_id = $("#user_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/shopcarts/"+user_id,
            contentType:"application/json",
            data: '',
        })

        ajax.done(function(res){
            $("#search_results").empty();
            $("#query_search_results").empty();
            clear_form_data()
            flash_message("All products in shopcart of User [" + res.user_id + "] have been Deleted!")
        });

        ajax.fail(function(res){
            $("#search_results").empty();
            $("#query_search_results").empty();
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#search_results").empty();
        $("#query_search_results").empty();
        clear_form_data()
    });


    // ****************************************
    // Query shopcarts for given amount
    // ****************************************

    $("#search-btn").click(function () {
        var amount = $("#amount").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/shopcarts/users?amount="+amount,
            contentType:"application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#query_search_results").empty();
            $("#search_results").empty();
            $("#query_search_results").append('<table class="table-striped"><thead>');
            var header = '<tr>'
            header += '<th style="width:35%">User Id</th>'
            $("#query_search_results").append(header);
            for(var i = 0; i < res.length; i++) {
                users = res[i];
                var row = "<tr><td>"+users+"</td></tr>";
                $("#query_search_results").append(row);
            }

            $("#query_search_results").append('</thead></table>');
            $("#query_search_results").append(res.length)

            flash_message("Success")
        });

        ajax.fail(function(res){
            $("#query_search_results").empty();
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // *********************************************
    // get the total amount of user's shopcart
    // *********************************************
    $("#total-btn").click(function () {
        var user_id = $("#user_id").val();

        var ajax = $.ajax({
            type : "GET",
            url: "/shopcarts/"+user_id+"/total",
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res) {
           $("#query_search_results").empty();
           $("#search_results").empty();
           $("#search_results").append('<table class="table-striped"><thead>');
           var header = '<tr>'
           header +=  '<th style="width:35%">Total Amount</th></tr>'
           $("#search_results").append(header);
	   var obj = jQuery.parseJSON(res);
           var tot = obj.total_price;
           var row = "<tr><td>"+tot+"</td></tr>";
           $("#search_results").append(row+"</thead></table>");
           $("#search_results").append('<br><table class="table-striped" <thead>');
	   header = "<tr>"
	   header +=  '<th style="width:35%">Product</th><th style="width=30%">Quantity</th><th style="width:35%">Price</th></tr>'
           var products = obj.products;
	   $("#search_results").append(header);
	   for (var i = 0;i<products.length;i++) {
               product = products[i];
	       row = "<tr><td>"+product.product_id+"</td><td>"+product.quantity+"</td><td>"+product.price+"</td></tr>";
	       $("#search_results").append(row);
	   }
	   $("#search_results").append('</thead></table>');



           flash_message("Success")
       });
       ajax.fail(function(res){
          $("#search_results").empty();
          clear_form_data()
          flash_message(res.responseJSON.message)
       });
    });

})
