from sklearn.metrics import f1_score 
from statistics import harmonic_mean
from tensorflow.keras.layers import Concatenate, Conv2D, Conv2DTranspose, Input, MaxPooling2D, Softmax
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import SGD


def xview2_metric(y_true, y_pred):
    scores = f1_score(y_true, y_pred, average=None)
    localization = scores[0]
    damage = harmonic_mean(scores[1:])
    return 0.3 * localization + 0.7 * damage


def create_model(shape=(1024, 1024, 3,), n_classes=5):
    inputs = Input(shape=shape)

    # Begin contractive layers

    conv_1_1 = Conv2D(64, (3, 3), padding="same")(inputs)
    conv_1_2 = Conv2D(64, (3, 3), padding="same")(conv_1_1)
    pool_1 = MaxPooling2D(pool_size=(2, 2))(conv_1_2)

    conv_2_1 = Conv2D(128, (3, 3), padding="same")(pool_1)
    conv_2_2 = Conv2D(128, (3, 3), padding="same")(conv_2_1)
    pool_2 = MaxPooling2D(pool_size=(2, 2))(conv_2_2)

    conv_3_1 = Conv2D(256, (3, 3), padding="same")(pool_2)
    conv_3_2 = Conv2D(256, (3, 3), padding="same")(conv_3_1)
    pool_3 = MaxPooling2D(pool_size=(2, 2))(conv_3_2)

    conv_4_1 = Conv2D(512, (3, 3), padding="same")(pool_3)
    conv_4_2 = Conv2D(512, (3, 3), padding="same")(conv_4_1)
    pool_4 = MaxPooling2D(pool_size=(2, 2))(conv_4_2)

    # Base of the "U"

    conv_5_1 = Conv2D(1024, (3, 3), padding="same")(pool_4)
    conv_5_2 = Conv2D(1024, (3, 3), padding="same")(conv_5_1)

    # Begin expansive layers

    up_conv_6 = Conv2DTranspose(512, (2, 2), strides=(2, 2))(conv_5_2)
    concat_6 = Concatenate(axis=-1)([up_conv_6, conv_4_2])
    conv_6_1 = Conv2D(512, (3, 3), padding="same")(concat_6)
    conv_6_2 = Conv2D(512, (3, 3), padding="same")(conv_6_1)

    up_conv_7 = Conv2DTranspose(256, (2, 2), strides=(2, 2))(conv_6_2)
    concat_7 = Concatenate(axis=-1)([up_conv_7, conv_3_2])
    conv_7_1 = Conv2D(256, (3, 3), padding="same")(concat_7)
    conv_7_2 = Conv2D(256, (3, 3), padding="same")(conv_7_1)

    up_conv_8 = Conv2DTranspose(128, (2, 2), strides=(2, 2))(conv_7_2)
    concat_8 = Concatenate(axis=-1)([up_conv_8, conv_2_2])
    conv_8_1 = Conv2D(128, (3, 3), padding="same")(concat_8)
    conv_8_2 = Conv2D(128, (3, 3), padding="same")(conv_8_1)

    up_conv_9 = Conv2DTranspose(64, (2, 2), strides=(2, 2))(conv_8_2)
    concat_9 = Concatenate(axis=-1)([up_conv_9, conv_1_2])
    conv_9_1 = Conv2D(64, (3, 3), padding="same")(concat_9)
    conv_9_2 = Conv2D(64, (3, 3), padding="same")(conv_9_1)

    # Final 1x1 convolution and softmax

    conv_9_3 = Conv2D(n_classes, (1, 1), padding="same")(conv_9_2)
    outputs = Softmax(axis=-1)(conv_9_3)

    # Set up the optimizer and loss

    # TODO: Is categorical cross-entropy the correct loss function given the competition metric?
    # TODO: Tune the learning rate (value not given in U-Net paper)
    model = Model(inputs=inputs, outputs=outputs)
    optimizer = SGD(learning_rate=0.01, momentum=0.99)
    model.compile(optimizer=optimizer, loss="categorical_crossentropy", metrics=[xview2_metric])
    return model