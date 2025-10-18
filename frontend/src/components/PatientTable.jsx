// src/components/PatientTable.jsx
import { useEffect, useState } from "react";
import axiosClient from "../api/axiosClient";
import PatientDialog from "./PatientDialog";
import RecordButton from "./RecordButton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function PatientTable() {
  const [patients, setPatients] = useState([]);
  const [selected, setSelected] = useState(null);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchPatients = async () => {
    try {
      setLoading(true);
      const res = await axiosClient.get("/patients");
      setPatients(res.data);
    } catch (err) {
      console.error("Error fetching patients:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, []);

  const handleRowClick = (p) => {
    setSelected(p);
    setOpen(true);
  };

  return (
    <div className="p-6">
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle>Patient Records</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-gray-500 text-center py-6">Loading...</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="p-3 border-b">First Name</th>
                    <th className="p-3 border-b">Last Name</th>
                    <th className="p-3 border-b">Phone</th>
                    <th className="p-3 border-b">New Patient</th>
                  </tr>
                </thead>
                <tbody>
                  {patients.map((p) => (
                    <tr
                      key={p.id}
                      onClick={() => handleRowClick(p)}
                      className="cursor-pointer hover:bg-gray-50 transition-colors"
                    >
                      <td className="p-3 border-b">{p.first_name}</td>
                      <td className="p-3 border-b">{p.last_name}</td>
                      <td className="p-3 border-b">{p.phone_number}</td>
                      <td className="p-3 border-b">
                        {p.new_patient ? (
                          <span className="text-green-600 font-medium">New</span>
                        ) : (
                          <span className="text-blue-600 font-medium">
                            Returning
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <PatientDialog
        open={open}
        onOpenChange={setOpen}
        patient={selected}
      />

      <RecordButton onAdded={fetchPatients} />
    </div>
  );
}