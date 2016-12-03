import dispatcher from "../dispatcher";
import constants from "../constants";

let GraphActionCreators = {
    setNumGraphs(...args){
        dispatcher.dispatch({
           type: constants.SET_NUM_GRAPHS,
           payload: {args} 
        });
    },
    setMyNum(...args){
        dispatcher.dispatch({
           type: constants.SET_MY_NUM,
           payload: {args} 
        });
    }
};



export default GraphActionCreators;
