import React from "react";
import {Router, Route, hashHistory} from 'react-router';
import {render} from "react-dom";

import BackpackGraphSelect from "./components/BackpackGraphSelect";

const app = document.getElementById("appId");

render((
    <BackpackGraphSelect/>
),app);
