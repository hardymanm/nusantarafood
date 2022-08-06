import {BrowserRouter, Routes, Route} from "react-router-dom";

import './App.css'
import Home from "./pages/home/index.jsx";
import Layout from "./pages/Layout.jsx";
import JudgeLayout from "./pages/judge/layout.jsx";
import JudgeWordNet from "./pages/judge/wordnet.jsx";
import JudgeWikipedia from "./pages/judge/wikipedia.jsx";
import JudgeTabel from "./pages/judge/tabel.jsx";
import Contribute from "./pages/home/contribute";
import ContactUs from "./pages/home/contact-us";
import Login from "./pages/home/login";
import DatasetWordNet from "./pages/judge/dataset-wordnet";
import DatasetWikipedia from "./pages/judge/dataset-wikipedia.jsx";
import DatasetTabel from "./pages/judge/dataset-tabel.jsx";


function AdminLayout() {
    return null;
}

function Pipeline() {
    return null;
}


function App() {

    return <BrowserRouter>
        <Routes>
            <Route path="/admin" element={<AdminLayout/>}>
                <Route index element={<Pipeline/>}/>
            </Route>
            <Route path="/judge" element={<JudgeLayout/>}>
                <Route path="dataset-wordnet" element={<DatasetWordNet/>}/>
                <Route path="dataset-wikipedia" element={<DatasetWikipedia/>}/>
                <Route path="dataset-tabel" element={<DatasetTabel/>}/>
                <Route path="wordnet" element={<JudgeWordNet/>}/>
                <Route path="wikipedia" element={<JudgeWikipedia/>}/>
                <Route path="tabel1981" element={<JudgeTabel/>}/>
            </Route>
            <Route path="/login" element={<Login/>}/>
            <Route path="/" element={<Layout/>}>
                <Route index element={<Home/>}/>
                <Route path="contact-us" element={<ContactUs/>}/>
                <Route path="contribute" element={<Contribute/>}/>
            </Route>
        </Routes>
    </BrowserRouter>
}

export default App
