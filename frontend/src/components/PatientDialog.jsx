// src/components/PatientDialog.jsx
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

export default function PatientDialog({ open, onOpenChange, patient }) {
  if (!patient) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {patient.first_name} {patient.last_name}
          </DialogTitle>
        </DialogHeader>
        <div className="mt-4 space-y-2">
          <p><strong>Phone:</strong> {patient.phone_number}</p>
          <p><strong>Address:</strong> {patient.address}</p>
          <p><strong>Status:</strong>{" "}
            {patient.new_patient ? "New Patient" : "Returning"}</p>
        </div>
      </DialogContent>
    </Dialog>
  );
}