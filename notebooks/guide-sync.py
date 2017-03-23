import sys
sys.path.insert(0, "../src") # the program is placed in subdirectory of project's root

import haydi as hd

class DfaLTS(hd.DLTS):
    def __init__(self, deltaf, actions):
        hd.DLTS.__init__(self, actions)
        self.deltaf = deltaf

    def step(self, state, action):
        return self.deltaf[(state, action)]


def compute(nstates, nsymbols):
    states = hd.Range(nstates)
    alphabet = hd.Range(nsymbols)

    def is_weakly_connected(dfa):
        # prepare undirected version
        ugraph = []

        for ((s1, a), s2) in dfa.iteritems():
            ugraph.append((s1, s2))
            ugraph.append((s2, s1))

        print "u-graph-a-: ", ugraph
        print set(ugraph)
        ugraph = dict(ugraph)

        print "u-graph-b-: ", ugraph

        # check connectiveness
        new_states = [0]
        processed = set()

        while new_states:
            cs = new_states.pop()
            processed.add(cs)

            # if len(processed) == nstates:
            #     break

            ns = ugraph[cs]
            if ns not in processed:
                new_states.append(ns)

        return processed == set(states)

    def is_synchronizable(dfa):
        # if not are_all_states_covered(dfa):
        #     return False

        max = nstates ** 2
        dfa_lts = DfaLTS(dfa, alphabet)
        synchronizable_pairs = set()

        def are_states_synchronizeable((s1, s2)):
            # both states represents the same one or
            # they alredy been marked as synchronizable
            return (s1 == s2) or (s1, s2) in synchronizable_pairs

        lts_pair = dfa_lts * dfa_lts
        state_pairs = hd.Product((states, states), unordered=True)
        for spair in state_pairs:
            witness = lts_pair.bfs(spair, max) \
                        .filter(are_states_synchronizeable) \
                        .first() \
                        .run()

            if witness is None:
                return False # non-synchronizable DFA

            # mark the pair of states as synchronizeable
            synchronizable_pairs.add(spair)
        return True

    def compute_shortest_sync_word(delta_f):
        dfa = DfaLTS(delta_f, alphabet)
        dfa_n_tuple = hd.DLTSProduct(tuple(dfa for i in range(nstates)))

        init_state = tuple(range(nstates))
        is_final = lambda (states, path): len(set(states)) == 1 # singleton state
        is_shortest = lambda (states, path): -len(path)

        # (1) run BFS procedure
        # (2) filter only those paths that leads a final state
        # (3) take only shortest paths
        witnesses = dfa_n_tuple.bfs_path(init_state)\
                                .filter(is_final)\
                                .max_all(is_shortest).run()

        if witnesses is None:
            print "none witness"
            return None

        sync_state, path = witnesses[0]
        #(transition function, the length of the shortest path, path, and synchronizing state)
        return (delta_f, len(path), path, sync_state)

    lrule = hd.Product((states, alphabet))
    deltaf = hd.Mapping(lrule, states)

    return deltaf.map(lambda dfa: (dfa, is_weakly_connected(dfa), is_synchronizable(dfa)))


if __name__ == "__main__":
    results = compute(3, 2)
    i = 0
    j = 0
    for dfa, covered, synced in results:
        i += 1
        if synced and not covered:
            j += 1
            print "{}: {}/{}".format(i, synced, covered)
            print "{}-dfa: {}".format(i, dfa)

    print "# of results {} / # of sync and not covered {}".format(i, j)
