const hostname = '127.0.0.1';
const port = 3000;
const { image } = require("@tensorflow/tfjs-node");
const unet = require("./model/unet.js");
const express = require('express');
const fileMiddleware = require("express-fileupload");
const app = express();
const path = require("path");
const tf = require("@tensorflow/tfjs-node");
const boundary = require("./model/boundary_box/boundary_processing.js");

app.use(express.static("public"));
app.use(fileMiddleware());
app.get('/', (request, response) => {
	response.sendFile(path.join(__dirname, './public/index.html'));
});
async function loadModel() {
	return await tf.loadLayersModel("file://model/pretrained/model.json");
}

const model = loadModel();

app.post('/example/predict', async (request, response) => {

	const { car_photo } = request.files;
	if(!car_photo) {
		response.sendStatus(400);
		return;
	}

	unet.predict(model, car_photo, (result) => {
		let imageBuffer = Buffer.from(car_photo.data);
		let maskBuffer = Buffer.from(result);

		if(maskBuffer && imageBuffer) {
			boundary.get_boundary_image(imageBuffer.toString("base64"),maskBuffer.toString('base64')).then((boundary) => {
				let boundaryBox = Buffer.from(boundary);
				response.status(200).send({image: imageBuffer.toString("base64"), mask: maskBuffer.toString('base64'), boundary: boundaryBox.toString('base64')});
			});

		} else {
			response.status(400);
		}
		
	});
});

app.listen(port, (error) => {
	if(error) {
		console.log(error);
		return;
	}
	console.log(`Server started at http://${hostname}:${port}/`);
});