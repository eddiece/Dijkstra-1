#ifndef _STATES_H_
#define _STATES_H_

#include "graph.h"

typedef enum state {
  NOT_VISITED,
  VISITING,
  VISITED
} state_t;

typedef struct nodes_states {
  int nb_members;
  state_t *states;
} states_t;


states_t *initStates(graph_t *graph);
void destroyStates(states_t *states);
void markNode(states_t *states, int v, state_t state);
int isState(states_t* states, int v, state_t state);

#endif  // _STATES_H_
