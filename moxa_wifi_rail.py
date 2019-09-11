import networkx

def get_edges( nodes: list, interference_level: int = 1 ) -> list:
    edges_1 = [ ( nodes[ i - 1 ], nodes[ i ] ) for i in range( 1, len( nodes ) ) ]
    print( len( edges_1 ) , edges_1 )
    edges = edges_1
    if interference_level == 2:
        edges_2 = [ ( nodes[ i - 2 ], nodes[ i ] ) for i in range( 2, len( nodes ) ) ]
        print( len( edges_2 ) , edges_2 )
        edges += edges_2
    return edges

# Metro R Line
def get_R_Line( n_segment: int = 10, interference_level: int = 1 ) -> ( list, list ):
    nodes = [ 'R%02d.%d' % ( i, j ) for i in range( 2, 28 + 1 ) for j in range( n_segment ) ]
    return nodes, get_edges( nodes, interference_level )

# Metro G Line
def get_G_Line( n_segment: int = 10, interference_level: int = 1 ) -> ( list, list ):
    nodes = [ 'G%02d.%d' % ( i, j ) for i in range( 1, 19 + 1 ) for j in range( n_segment ) ]
    return nodes, get_edges( nodes, interference_level )

def get_cross_edges( nodes_R: list, nodes_G: list, n_segment: int = 10, interference_level: int = 1 ) -> list:
    # R08 x G10
    id_R08 =  8 - 2; id_G10 = 10 - 1
    id_R11 = 11 - 2; id_G14 = 14 - 1

    edges_cross = []
    if interference_level >= 1:
        edges_cross += [ ( nodes_R[ id_R08 * n_segment + i ], nodes_G[ id_G10 * n_segment + j ] ) for i in ( -1, 0, 1 ) for j in ( -1, 0, 1 ) ]
        edges_cross += [ ( nodes_R[ id_R11 * n_segment + i ], nodes_G[ id_G14 * n_segment + j ] ) for i in ( -1, 0, 1 ) for j in ( -1, 0, 1 ) ]
    if interference_level >= 2:
        edges_cross += [ ( nodes_R[ id_R08 * n_segment + 0 ], nodes_G[ id_G10 * n_segment - 2 ] ),  # R08.0
                         ( nodes_R[ id_R08 * n_segment + 0 ], nodes_G[ id_G10 * n_segment + 2 ] ),
                         ( nodes_R[ id_R08 * n_segment + 2 ], nodes_G[ id_G10 * n_segment + 0 ] ),  # G10.0
                         ( nodes_R[ id_R08 * n_segment - 2 ], nodes_G[ id_G10 * n_segment + 0 ] ) ]
        edges_cross += [ ( nodes_R[ id_R11 * n_segment + 0 ], nodes_G[ id_G14 * n_segment - 2 ] ),  # R11.0
                         ( nodes_R[ id_R11 * n_segment + 0 ], nodes_G[ id_G14 * n_segment + 2 ] ),
                         ( nodes_R[ id_R11 * n_segment + 2 ], nodes_G[ id_G14 * n_segment + 0 ] ),  # G14.0
                         ( nodes_R[ id_R11 * n_segment - 2 ], nodes_G[ id_G14 * n_segment + 0 ] ) ]
    return edges_cross

def show_nodes_attributes( graph: networkx.classes.graph.Graph ):
    for node in graph.nodes:
        print( node, graph.degree( node ), graph.nodes[ node ] )

def get_node_available_channels_prioritized( graph: networkx.classes.graph.Graph, node: str ) -> list:
    available_channels_prioritized = []
    if 'available_channels_prioritized' in graph.nodes[ node ]:
        available_channels_prioritized = graph.nodes[ node ][ 'available_channels_prioritized' ].split( ',' )
    return available_channels_prioritized

def set_node_available_channels_prioritized( graph: networkx.classes.graph.Graph, node: str, available_channels_prioritized: list ):
    graph.nodes[ node ][ 'available_channels_prioritized' ] = available_channels_prioritized

def get_node_current_channel( graph: networkx.classes.graph.Graph, node: str ) -> str:
    if 'current_channel' in graph.nodes[ node ]:
        return graph.nodes[ node ][ 'current_channel' ]
    else:
        return None

def set_node_current_channel( graph: networkx.classes.graph.Graph, node: str, current_channel: str ):
    graph.nodes[ node ][ 'current_channel' ] = current_channel

def clear_nodes_current_channels( graph: networkx.classes.graph.Graph, nodes: list ):
    for node in nodes:
        if get_node_current_channel( graph, node ):
            set_node_current_channel( graph, node, '' )

def get_nodes_sorted_for_config( graph: networkx.classes.graph.Graph, nodes: list ) -> list:
    #
    # High Degree First, Low Available Channels First
    #
    def get_priority( node: str ) -> float:
        priority = graph.degree( node )
        available_channels_list = get_node_available_channels_prioritized( graph, node )
        if available_channels_list:
            priority += 1 / len( available_channels_list )
        else:
            priority += 0 # least priority among same degree nodes
        # node_dict = graph.nodes[ node ]
        # if ( 'available_channels_prioritized' in node_dict ) and ( len( node_dict[ 'available_channels_prioritized' ] ) != 0 ):
        #     priority += 1 / len( node_dict[ 'available_channels_prioritized' ] ) # less available channels, more weight
        # else:
        #     priority += 0 # least priority among same degree nodes
        return priority
    return sorted( nodes, key = get_priority, reverse = True )
    #
    #  Low Degree First, Low Available Channels First
    #
    # def get_priority( node_name ) -> float:
    #     priority = graph.degree( node_name ) * 100 # to avoid mixing with 2nd criteria
    #     node_dict = graph.nodes[ node_name ]
    #     if 'available_channels_prioritized' in node_dict and ( len( node_dict[ 'available_channels_prioritized' ] ) != 0 ):
    #         priority += len( node_dict[ 'available_channels_prioritized' ] ) # less available channels, more weight
    #     else:
    #         priority += 0 # least priority among same degree nodes
    #     return priority
    # return sorted( graph.nodes, key = get_priority, reverse = False )

def initialize_nodes_available_channels( graph: networkx.classes.graph.Graph, channels: str = '1,3,5,7,9,11' ):
    full_channels_list = [ i for i in range( 1, 11 ) ]
    
    # initialize 'available_channels_prioritized'
    for i, node in enumerate( graph.nodes ):
        set_node_available_channels_prioritized( graph, node, channels )
        # if i < 5:
        #     #set_node_available_channels_prioritized( g_metro_sub, node, [ '1', '4', '7', '10' ] )
        #     set_node_available_channels_prioritized( g_metro_sub, node, '1,4,7,10' )
        # elif i < 10:
        #     #set_node_available_channels_prioritized( g_metro_sub, node, [ '2', '5', '8' ] )
        #     set_node_available_channels_prioritized( g_metro_sub, node, '2,5,8' )
        # else:
        #     #set_node_available_channels_prioritized( g_metro_sub, node, full_channels_list )
        #     set_node_available_channels_prioritized( g_metro_sub, node, ','.join( full_channels_list ) )

def select_preferred_channel( available_channels: list ) -> str:
    print( available_channels )
    return available_channels[ 0 ]

def configure_node_current_channel( graph: networkx.classes.graph.Graph, node: str ):
    available_channels = get_node_available_channels_prioritized( graph, node )
    for neighbor in graph.neighbors( node ):
        neighbor_channel = get_node_current_channel( graph, neighbor )
        
        #available_channels = numpy.setdiff1d( available_channels, neighbor_channel ) 
        if neighbor_channel in available_channels:
            available_channels.remove( neighbor_channel ) # avoid interference

    if len( available_channels ) > 0:
        set_node_current_channel( graph, node, select_preferred_channel( available_channels ) )
    else:
        # raise ValueError( 'Not enough available channels to avoid interference.' )
        print( 'Not enough available channels to avoid interference.' )
        set_node_current_channel( graph, node, '' )

def configure_nodes_current_channel( graph: networkx.classes.graph.Graph, nodes: list ):
    # Since these nodes request for configuration, their current channels are no longer valid and can be cleared.
    clear_nodes_current_channels( graph, nodes )

    # configure 'current_channel'
    nodes = get_nodes_sorted_for_config( graph, nodes )
    for node in nodes:
        configure_node_current_channel( graph, node )
        print( node, get_node_current_channel( graph, node ) )

def check_interference( graph: networkx.classes.graph.Graph, node: str ):
    print( node, get_node_current_channel( graph, node ),
           [ ( neighbor, get_node_current_channel( graph, neighbor ) ) for neighbor in graph.neighbors( node ) ] )

def check_system_channels_configuration( graph: networkx.classes.graph.Graph ):
    w_current_channel_list, wo_current_channel_list = [], []
    for node in graph.nodes:
        current_channel = get_node_current_channel( graph, node )
        if current_channel:
            w_current_channel_list.append( node )
        else:
            wo_current_channel_list.append( node )
    print( 'node(s) with current channels:', w_current_channel_list )
    print( 'node(s) w/o current channels:', wo_current_channel_list )
