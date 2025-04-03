$(document).ready(function () {
    // Role-based field display
    $('#user_type').change(function () {
        if ($(this).val() === 'Pet Owner') {
            $('#customerFields').show();
            $('#serviceProviderFields').hide();
        } else {
            $('#customerFields').hide();
            $('#serviceProviderFields').show();
        }
    }).trigger('change');

    // Handle form submissions (Signup, Login, Admin Login)
    $('#signupForm, #loginForm, #adminLoginForm').submit(function (event) {
        event.preventDefault();  
        let formData = $(this).serialize();  
        let action = $(this).attr('action');  
        console.log("Submitting to:", action);
        console.log("Data Sent:", formData);

        $.post(action, formData, function (response) {
            console.log("Response:", response);
            alert(response.message);
            if (response.status === "success") {
            window.location.href = response.redirect;  // Redirect to dashboard
        }
        }).fail(function (xhr, status, error) {
            console.log("Error:", error, "| Status:", status);
            console.log("Server Response:", xhr.responseText);
            alert('Error processing request. Please try again.');
        });
    });

    // Forgot Password Toggle
    $("#forgotPasswordLink").click(function(e) {
        e.preventDefault();
        $("#loginSection").hide(); // Hide login form
        $("#forgotPasswordSection").fadeIn(); // Show reset section
    });

    $("#backToLogin").click(function() {
        $("#forgotPasswordSection").fadeOut(function() {
            $("#loginSection").fadeIn(); // Show login form again
        });
    });

    // Reset Password Functionality
    $('#resetPasswordBtn').click(function () {
        let email = $('#resetEmail').val().trim();
        if (email === '') {
            alert('Please enter your email to reset the password.');
            return;
        }

        $.post('/reset-password', { email: email }, function (response) {
            alert(response.message);
            $('#forgotPasswordSection').fadeOut();
            $('#forgotPasswordLink').fadeIn();
        }).fail(function () {
            alert('Error resetting password. Please try again.');
        });
    });

    // Function to handle tab switching with event prevention
    function showTab(tabId, event) {
        event.preventDefault(); // Prevent default anchor behavior
        let tab = new bootstrap.Tab(document.querySelector('[href="#' + tabId + '"]'));
        tab.show();
    }

    // Ensure Admin Login tab activates when clicked
    $('a[href="#admin-login"]').click(function(event) {
        showTab('admin-login', event);
    });
});
