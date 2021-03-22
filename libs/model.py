from keras.models import *
from keras.layers import *
from keras.optimizers import *
from keras.initializers import *
from keras.regularizers import *
from tensorflow.keras.utils import plot_model
import tensorflow as tf

physical_devices = tf.config.list_physical_devices('GPU')
try:
  tf.config.experimental.set_memory_growth(physical_devices[0], True)
except:
  pass

class NN(Model):
    def __init__(self, num_observations, num_actions, num_values, game_size, lr_actor, lr_critic):
        super(NN, self).__init__()
        self.num_observations = num_observations
        self.num_actions = num_actions
        self.num_values = num_values
        self.game_size = game_size
        self.lr_actor = lr_actor
        self.lr_critic = lr_critic

        state = Input(shape=self.num_observations, name='Input')
        game = Input(shape=self.game_size, name='Input_game')

        x = Dense(128, kernel_regularizer=l2(1e3))(state)
        x = Activation('relu')(x)
        x = Dense(32, kernel_regularizer=l2(1e3))(state)
        x = Activation('relu')(x)
        x = Flatten()(x)

        w = Dense(128, kernel_regularizer=l2(1e3))(game)
        w = Dense(32, kernel_regularizer=l2(1e3))(w)
        w = Activation('relu')(w)
        w = Flatten()(w)

        x = Concatenate()([x, w])

        actor_in = Dense(64, activation='relu')(x)
        actor_out = Dense(self.num_actions,
                         activation='softmax',
                         name='Dense_Actor_1')(actor_in)
        self.actor = Model(inputs=[state, game], outputs=actor_out)
        self.actor.summary()
        self.actor.compile(loss="categorical_crossentropy", optimizer=Adam(lr=self.lr_actor))
        plot_model(self.actor, to_file='./1_model/Actor.png',
                    show_shapes=True, show_dtype=True,
                    show_layer_names=True) 

        critic_x = Dense(64, activation='relu', name='Dense_cr')(x)
        critic_out = Dense(self.num_values, activation='linear')(critic_x)
        self.critic = Model(inputs=[state, game], outputs=critic_out)
        self.critic.summary()
        self.critic.compile(loss="mse", optimizer=Adam(lr=self.lr_critic))       
        plot_model(self.critic, to_file='./1_model/Critic.png',
                    show_shapes=True, show_dtype=True,
                    show_layer_names=True) 

    # Actor Functions
    def train_actor(self, states, games, advantages):
        self.actor.fit(x=[states, games], y=advantages, verbose=0, epochs=1)

    def predict_actor(self, states):
        return self.actor(states)

    # Critic Functions
    def train_critic(self, states, games, values):
        self.critic.fit(x=[states, games], y=values, verbose=0, epochs=1)

    def predict_critic(self, states):
        return self.critic(states)