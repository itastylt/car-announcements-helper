let canvas = document.getElementById("photo_prediction");
let ctx = canvas.getContext('2d');

let boundary_canvas = document.getElementById("boundary_prediction");
let boundary_ctx = boundary_canvas.getContext('2d');

jQuery("#camera-form").on("submit", (e) => {
    e.preventDefault();
    jQuery("#app-main").addClass('d-none');
    jQuery("#loader").removeClass('d-none');
    $.ajax( {
        type: "POST",
        url: "/example/predict",
        data: new FormData(document.getElementById("camera-form")),
        processData: false,
        contentType: false,
        cache:false,
        success: (data) => {
            var image = new Image();
            image.onload = function() {
                ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
            };
            jQuery("#photo_prediction").removeClass("d-none");
            jQuery("#camera-form").addClass("d-none");
            image.src = `data:image/png;base64,${data.image}`;
            image.onload = function() {
                ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
            };
            let boundary = new Image();
            boundary.onload = function() {
                boundary_ctx.drawImage(boundary, 0, 0, boundary_canvas.width, boundary_canvas.height);
            }
            boundary.src = `data:image/png;base64, ${data.boundary}`;
            var mask = new Image();
            ctx.globalAlpha = 0.4;
            mask.onload = function() {
                ctx.drawImage(mask, 0, 0, canvas.width, canvas.height);
            };
            mask.src = `data:image/png;base64,${data.mask}`;

            jQuery("#loader").addClass('d-none');
            jQuery("#app-main").removeClass('d-none');
        },
        error: (error) => {
            console.log(error);
        }
    });
});


