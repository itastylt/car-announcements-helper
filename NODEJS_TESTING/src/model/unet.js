const tf = require("@tensorflow/tfjs-node");

module.exports = {
    predict: 
        async (imageBuffer) => {
            const model = await tf.loadLayersModel("file://model/pretrained/model.json");

            if(imageBuffer != null) {
                try {
                    const imageTensor = tf.node.decodePng(imageBuffer.data, 3);
                    const sample = tf.image.resizeBilinear(imageTensor, [256, 256]);
                    let prediction = model.predict(sample.reshape([1, 256, 256, 3]));
                    let prediction_presampling = prediction.sub(tf.min(prediction));
                    prediction_presampling = prediction_presampling.reshape([256, 256, 1]);
                    prediction_presampling = tf.image.grayscaleToRGB(prediction_presampling.reshape([256,256, 1]));
                    let zeros = tf.zeros(prediction_presampling.shape);
                    let blackPixels = tf.greater(prediction_presampling, zeros);
                    prediction_presampling = prediction_presampling.where(blackPixels, zeros);
                    let ones = tf.ones(prediction_presampling.shape).mul(0.5);
                    let whitePixels = tf.greater(prediction_presampling, ones);
                    prediction_presampling = ones.where(whitePixels, prediction_presampling).mul(2);
                    prediction_presampling = tf.image.resizeBilinear(prediction_presampling, [512, 512]);

                    let prediction_sample = prediction_presampling.mul(255);
                    if(prediction) {
                        return await tf.node.encodePng(prediction_sample.reshape([512, 512, 3]));
                    }

                } catch (error) {
                    console.log(error);
                }
            } else {
                console.log("No image provided.");
            }
        }
}