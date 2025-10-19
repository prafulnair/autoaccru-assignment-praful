import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";

export default function PatientDialog({ open, onOpenChange, patient }) {
  if (!patient) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className="
          sm:max-w-[400px] w-[90%]
          bg-white/90 backdrop-blur-md
          rounded-2xl border border-gray-200 shadow-xl
          p-6 transition-all duration-300
        "
      >
        <DialogHeader className="pb-2 border-b">
          <DialogTitle className="text-lg font-semibold text-gray-900 text-center">
            {patient.first_name} {patient.last_name}
          </DialogTitle>
          <DialogDescription className="text-sm text-gray-500 text-center">
            Patient ID: {patient.id}
          </DialogDescription>
        </DialogHeader>

        <div className="mt-4 grid gap-3 text-sm text-gray-700">
          <div className="flex justify-between">
            <span className="font-medium text-gray-800">Phone:</span>
            <span>{patient.phone_number}</span>
          </div>
          <div className="flex justify-between">
            <span className="font-medium text-gray-800">Address:</span>
            <span className="text-right max-w-[60%]">{patient.address}</span>
          </div>
          <div className="flex justify-between">
            <span className="font-medium text-gray-800">Status:</span>
            <span className={`font-semibold ${patient.new_patient ? "text-green-600" : "text-blue-600"}`}>
              {patient.new_patient ? "New Patient" : "Returning Patient"}
            </span>
          </div>
        </div>

        <DialogFooter className="pt-5 border-t">
          <DialogClose asChild>
            <button className="w-full rounded-lg border px-4 py-2 text-sm hover:bg-gray-100">
              Close
            </button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}