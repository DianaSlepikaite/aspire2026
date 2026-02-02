import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Briefcase, Building2, Calendar, Mail, MapPin, Phone } from "lucide-react";
import { EditableTextField } from "@/components/layout/core/EditableTextField";

interface PersonalRoleSectionProps {
  editingField: string | null;
  setEditingField: (field: string | null) => void;
  fullNameDraft: string;
  setFullNameDraft: (value: string) => void;
  emailDraft: string;
  setEmailDraft: (value: string) => void;
  phoneDraft: string;
  setPhoneDraft: (value: string) => void;
  locationDraft: string;
  setLocationDraft: (value: string) => void;
  titleDraft: string;
  setTitleDraft: (value: string) => void;
  departmentDraft: string;
  setDepartmentDraft: (value: string) => void;
  managerDraft: string;
  setManagerDraft: (value: string) => void;
  startDateDraft: string;
  setStartDateDraft: (value: string) => void;
  employmentTypeDraft: string;
  setEmploymentTypeDraft: (value: string) => void;
}

export function PersonalRoleSection({
  editingField,
  setEditingField,
  fullNameDraft,
  setFullNameDraft,
  emailDraft,
  setEmailDraft,
  phoneDraft,
  setPhoneDraft,
  locationDraft,
  setLocationDraft,
  titleDraft,
  setTitleDraft,
  departmentDraft,
  setDepartmentDraft,
  managerDraft,
  setManagerDraft,
  startDateDraft,
  setStartDateDraft,
  employmentTypeDraft,
  setEmploymentTypeDraft,
}: PersonalRoleSectionProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-card rounded-2xl border border-border p-6 space-y-5">
        <div className="flex items-center justify-between">
          <h4 className="text-lg font-semibold">Personal & Contact</h4>
          <Badge variant="secondary">Editable</Badge>
        </div>
        <p id="core-editing-hint" className="sr-only">
          Press Enter to edit a field. Use Tab to move between fields.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label
              htmlFor="core-full-name"
              id="core-full-name-label"
              className="text-xs font-semibold text-muted-foreground uppercase"
            >
              Full Name
            </label>
            <EditableTextField
              field="full_name"
              value={fullNameDraft}
              placeholder="Full name"
              onChange={setFullNameDraft}
              editingField={editingField}
              setEditingField={setEditingField}
              displayClassName="max-w-full"
              inputId="core-full-name"
              labelId="core-full-name-label"
              ariaLabel="Full name"
              describedById="core-editing-hint"
            />
          </div>
          <div>
            <label
              htmlFor="core-location"
              id="core-location-label"
              className="text-xs font-semibold text-muted-foreground uppercase"
            >
              Location
            </label>
            <div className="relative">
              <MapPin className="size-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
              {editingField === "location" ? (
                <Input
                  id="core-location"
                  className="pl-9"
                  value={locationDraft}
                  onChange={(event) => setLocationDraft(event.target.value)}
                  onBlur={() => setEditingField(null)}
                  aria-labelledby="core-location-label"
                  aria-describedby="core-editing-hint"
                />
              ) : (
                <button
                  type="button"
                  className="min-h-[40px] w-full rounded-md border border-border pl-9 pr-3 py-2 text-left text-sm hover:bg-secondary/30 transition-colors truncate"
                  onClick={() => setEditingField("location")}
                  title={locationDraft}
                  aria-labelledby="core-location-label"
                  aria-describedby="core-editing-hint"
                >
                  {locationDraft || <span className="text-muted-foreground">Location</span>}
                </button>
              )}
            </div>
          </div>
          <div>
            <label
              htmlFor="core-email"
              id="core-email-label"
              className="text-xs font-semibold text-muted-foreground uppercase"
            >
              Email
            </label>
            <div className="relative">
              <Mail className="size-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
              {editingField === "email" ? (
                <Input
                  id="core-email"
                  className="pl-9"
                  value={emailDraft}
                  onChange={(event) => setEmailDraft(event.target.value)}
                  onBlur={() => setEditingField(null)}
                  aria-labelledby="core-email-label"
                  aria-describedby="core-editing-hint"
                />
              ) : (
                <button
                  type="button"
                  className="min-h-[40px] w-full rounded-md border border-border pl-9 pr-3 py-2 text-left text-sm hover:bg-secondary/30 transition-colors truncate"
                  onClick={() => setEditingField("email")}
                  title={emailDraft}
                  aria-labelledby="core-email-label"
                  aria-describedby="core-editing-hint"
                >
                  {emailDraft || <span className="text-muted-foreground">Email</span>}
                </button>
              )}
            </div>
          </div>
          <div>
            <label
              htmlFor="core-phone"
              id="core-phone-label"
              className="text-xs font-semibold text-muted-foreground uppercase"
            >
              Phone
            </label>
            <div className="relative">
              <Phone className="size-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
              {editingField === "phone" ? (
                <Input
                  id="core-phone"
                  className="pl-9"
                  value={phoneDraft}
                  onChange={(event) => setPhoneDraft(event.target.value)}
                  onBlur={() => setEditingField(null)}
                  aria-labelledby="core-phone-label"
                  aria-describedby="core-editing-hint"
                />
              ) : (
                <button
                  type="button"
                  className="min-h-[40px] w-full rounded-md border border-border pl-9 pr-3 py-2 text-left text-sm hover:bg-secondary/30 transition-colors truncate"
                  onClick={() => setEditingField("phone")}
                  title={phoneDraft}
                  aria-labelledby="core-phone-label"
                  aria-describedby="core-editing-hint"
                >
                  {phoneDraft || <span className="text-muted-foreground">Phone</span>}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="bg-card rounded-2xl border border-border p-6 space-y-5">
        <div className="flex items-center justify-between">
          <h4 className="text-lg font-semibold">Role & Org</h4>
          <Badge variant="secondary">Editable</Badge>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label
              htmlFor="core-title"
              id="core-title-label"
              className="text-xs font-semibold text-muted-foreground uppercase"
            >
              Title
            </label>
            <div className="relative">
              <Briefcase className="size-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
              {editingField === "title" ? (
                <Input
                  id="core-title"
                  className="pl-9"
                  value={titleDraft}
                  onChange={(event) => setTitleDraft(event.target.value)}
                  onBlur={() => setEditingField(null)}
                  aria-labelledby="core-title-label"
                  aria-describedby="core-editing-hint"
                />
              ) : (
                <button
                  type="button"
                  className="min-h-[40px] w-full rounded-md border border-border pl-9 pr-3 py-2 text-left text-sm hover:bg-secondary/30 transition-colors truncate"
                  onClick={() => setEditingField("title")}
                  title={titleDraft}
                  aria-labelledby="core-title-label"
                  aria-describedby="core-editing-hint"
                >
                  {titleDraft || <span className="text-muted-foreground">Title</span>}
                </button>
              )}
            </div>
          </div>
          <div>
            <label
              htmlFor="core-department"
              id="core-department-label"
              className="text-xs font-semibold text-muted-foreground uppercase"
            >
              Department
            </label>
            <div className="relative">
              <Building2 className="size-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
              {editingField === "department" ? (
                <Input
                  id="core-department"
                  className="pl-9"
                  value={departmentDraft}
                  onChange={(event) => setDepartmentDraft(event.target.value)}
                  onBlur={() => setEditingField(null)}
                  aria-labelledby="core-department-label"
                  aria-describedby="core-editing-hint"
                />
              ) : (
                <button
                  type="button"
                  className="min-h-[40px] w-full rounded-md border border-border pl-9 pr-3 py-2 text-left text-sm hover:bg-secondary/30 transition-colors truncate"
                  onClick={() => setEditingField("department")}
                  title={departmentDraft}
                  aria-labelledby="core-department-label"
                  aria-describedby="core-editing-hint"
                >
                  {departmentDraft || <span className="text-muted-foreground">Department</span>}
                </button>
              )}
            </div>
          </div>
          <div>
            <label
              htmlFor="core-manager"
              id="core-manager-label"
              className="text-xs font-semibold text-muted-foreground uppercase"
            >
              Manager
            </label>
            <EditableTextField
              field="manager"
              value={managerDraft}
              placeholder="Manager"
              onChange={setManagerDraft}
              editingField={editingField}
              setEditingField={setEditingField}
              inputId="core-manager"
              labelId="core-manager-label"
              ariaLabel="Manager"
              describedById="core-editing-hint"
            />
          </div>
          <div>
            <label
              htmlFor="core-start-date"
              id="core-start-date-label"
              className="text-xs font-semibold text-muted-foreground uppercase"
            >
              Start Date
            </label>
            <div className="relative">
              <Calendar className="size-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
              {editingField === "startDate" ? (
                <Input
                  id="core-start-date"
                  className="pl-9"
                  value={startDateDraft}
                  onChange={(event) => setStartDateDraft(event.target.value)}
                  onBlur={() => setEditingField(null)}
                  aria-labelledby="core-start-date-label"
                  aria-describedby="core-editing-hint"
                />
              ) : (
                <button
                  type="button"
                  className="min-h-[40px] w-full rounded-md border border-border pl-9 pr-3 py-2 text-left text-sm hover:bg-secondary/30 transition-colors truncate"
                  onClick={() => setEditingField("startDate")}
                  title={startDateDraft}
                  aria-labelledby="core-start-date-label"
                  aria-describedby="core-editing-hint"
                >
                  {startDateDraft || <span className="text-muted-foreground">Start date</span>}
                </button>
              )}
            </div>
          </div>
          <div className="md:col-span-2">
            <label
              htmlFor="core-employment-type"
              id="core-employment-type-label"
              className="text-xs font-semibold text-muted-foreground uppercase"
            >
              Employment Type
            </label>
            <EditableTextField
              field="employmentType"
              value={employmentTypeDraft}
              placeholder="Employment type"
              onChange={setEmploymentTypeDraft}
              editingField={editingField}
              setEditingField={setEditingField}
              inputId="core-employment-type"
              labelId="core-employment-type-label"
              ariaLabel="Employment type"
              describedById="core-editing-hint"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
