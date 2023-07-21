const hostname = '127.0.0.1';
const port = 3000;
const { image } = require("@tensorflow/tfjs-node");
const unet = require("./model/unet.js");
const express = require('express');
const fileMiddleware = require("express-fileupload");
const app = express();
const path = require("path");

app.use(fileMiddleware());
app.get('/', (request, response) => {
	response.sendFile(path.join(__dirname, './public/index.html'));
});

app.post('/example/predict', async (request, response) => {
	const { image } = request.files;
	await image.mv(__dirname + "/model/temp/" + image.name);
	if(!image) {
		response.sendStatus(400);
		return;
	}

	unet.predict(image).then((result) => {
		var img = Buffer.from(result);

		response.writeHead(200, {
		  'Content-Type': 'image/png',
		  'Content-Length': img.length
		});
		response.end(img);
	});
});

app.listen(port, (error) => {
	if(error) {
		console.log(error);
		return;
	}
	console.log(`Server started at http://${hostname}:${port}/`);
});