const tf = require("@tensorflow/tfjs-node");

module.exports = {
    get_boundary_image:
        async (base64image, base64mask) => {
            if(!base64image || !base64mask) {
                return;
            }
            let image = Buffer.from(base64image, 'base64');
            let mask = Buffer.from(base64mask, 'base64');
            let imageTensor = tf.node.decodePng(image, 3);
            let maskTensor = tf.node.decodePng(mask, 1);

            imageTensor = tf.image.resizeBilinear(imageTensor, [256,256]);
            maskTensor = tf.image.resizeBilinear(maskTensor, [256, 256]);
            imageTensor = imageTensor.mean(2);
            imageTensor = imageTensor.reshape([256, 256, 1]);
            
            let imageArray = imageTensor.arraySync();
            let maskArray = maskTensor.arraySync();
            let firstx = 255;
            let firsty = 255;
            let lastx = 0;
            let lasty = 0;
            for(let x = 0; x < maskArray.length; x++) {
                for(let y = 0; y < maskArray[x].length; y++) {
                    if(maskArray[x][y][0] == 255) {
                        if(x < firstx) {
                            firstx = x;
                        }

                        lastx = x;
                        if(y < firsty) {
                            firsty = y;
                        }

                        if(y > lasty) {
                            lasty = y;
                        }
                    }
                }
            }
            
            let section = imageArray.slice(firstx, lastx).map(i => i.slice(firsty, lasty));
            let boundaryTensor = tf.tensor([section]);
            boundaryTensor = tf.image.resizeBilinear(boundaryTensor, [64, 64]);
            return await tf.node.encodePng(boundaryTensor.reshape([64, 64, 1]));
        }
}
