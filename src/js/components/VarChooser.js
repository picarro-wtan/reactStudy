import React, {Component, PropTypes} from "react";

export default class VarChooser extends Component {
    constructor(...args){
        super(...args);
    
    }
    
    
    render(){
      let options = this.props.variables.map( 
              (variable,idx) => (<option value = {variable} key = {idx}>{variable} </option>)
          );
      
      
      return (<div>
        Graph {this.props.graphIdx} 
        <select value = {this.props.selectedVar} onChange = { (e) => {this.props.userInput(e.target.value)}}>
            {options}
        </select>
      
      </div>);  
    };
    
}


 
 VarChooser.propTypes = {
     graphIdx: PropTypes.number.isRequired,
     variables: PropTypes.arrayOf(PropTypes.string).isRequired,
     selectedVar: PropTypes.string.isRequired,
     userInput: PropTypes.func.isRequired
 }