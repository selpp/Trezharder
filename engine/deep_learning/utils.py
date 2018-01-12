import tensorflow as tf

def conv2D(x, channels, kernel, stride, scope):
    in_channels = x.get_shape()[-1]
    with tf.variable_scope(scope):
        w = tf.get_variable(name='weights',
                            shape=[kernel[0], kernel[1], in_channels, channels],
                            initializer=tf.contrib.layers.xavier_initializer())
        b = tf.get_variable(name='biases',
                            shape=[channels],
                            initializer=tf.constant_initializer(0.0))
        x = tf.nn.conv2d(x, w, stride, padding='SAME', name='conv')
        x = tf.nn.bias_add(x, b, name='bias_add')
        x = tf.nn.relu(x, name='relu')
        return x

def dense(x, neurons, scope, activation_fn = tf.nn.relu):
    shape = x.get_shape()
    size = shape[-1].value

    with tf.variable_scope(scope):
        w = tf.get_variable('weights',
                            shape=[size, neurons],
                            initializer=tf.contrib.layers.xavier_initializer())
        b = tf.get_variable('biases',
                            shape=[neurons],
                            initializer=tf.constant_initializer(0.0))
        x = tf.nn.bias_add(tf.matmul(x, w), b)
        if activation_fn is not None:
            x = activation_fn(x)
        return x

def flatten(x, scope):
    shape = x.get_shape()
    size = shape[1].value * shape[2].value * shape[3].value

    with tf.variable_scope(scope):
        flat_x = tf.reshape(x, [-1, size])

    return flat_x
