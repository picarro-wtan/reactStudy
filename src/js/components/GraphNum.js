import React, {Component, PropTypes} from "react";
import GraphActionCreators from "../actions/GraphActionCreators";

export default class GraphNum extends Component {
    constructor(...args){
        super(...args);
        this.onChange= this.onChange.bind(this);
    }
    
    onChange(event){
        
        GraphActionCreators.setNumGraphs(+event.target.value);
    }
    
    render(){
      return (<div>Number of Graphs
        <select style = {{marginLeft: "20px"}} value = {this.props.nGraphs} onChange = {this.onChange}>
            <option value = {1}> 1 </option>
            <option value = {2}> 2 </option>
            <option value = {3}> 3 </option>
        </select>
      </div>);  
    };
    
}



 GraphNum.propTypes = {
     nGraphs:PropTypes.number.isRequired,
     userInput:PropTypes.func.isRequired
 }