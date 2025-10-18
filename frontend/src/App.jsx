import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import PatientTable from "./components/PatientTable";


export default function App() {
  return (
    <div className="min-h-screen bg-white text-gray-800">
      <PatientTable />
    </div>
  );
}

