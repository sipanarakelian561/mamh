import {BrowserRouter, Routes, Route} from 'react-router-dom'
import Home from './pages/home.jsx'
import './App.css'

export default function App() {
  return (
      <BrowserRouter>
        <div className="min-h-screen bg-gradient-to-b from-white to-black">
          <Routes>
            <Route path="/" element={<Home />} />
          </Routes>
        </div>
      </BrowserRouter>
  );
}