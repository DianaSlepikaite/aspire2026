import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus, X } from "lucide-react";

interface SkillsCertificationsSectionProps {
  skillsDraft: string[];
  certificationsDraft: string[];
  skillInput: string;
  certInput: string;
  setSkillInput: (value: string) => void;
  setCertInput: (value: string) => void;
  addSkill: () => void;
  removeSkill: (skill: string) => void;
  addCertification: () => void;
  removeCertification: (cert: string) => void;
}

export function SkillsCertificationsSection({
  skillsDraft,
  certificationsDraft,
  skillInput,
  certInput,
  setSkillInput,
  setCertInput,
  addSkill,
  removeSkill,
  addCertification,
  removeCertification,
}: SkillsCertificationsSectionProps) {
  return (
    <div className="bg-card rounded-2xl border border-border p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-lg font-semibold">Skills & Certifications</h4>
        <Badge variant="secondary">Editable</Badge>
      </div>
      <div>
        <label
          htmlFor="core-skill-input"
          id="core-skill-input-label"
          className="text-xs font-semibold text-muted-foreground uppercase"
        >
          Top Skills
        </label>
        <div className="flex flex-wrap gap-2 mt-2">
          {skillsDraft.map((skill) => (
            <Badge key={skill} variant="outline" className="flex items-center gap-1">
              {skill}
              <button
                type="button"
                className="ml-1 text-muted-foreground hover:text-foreground"
                onClick={() => removeSkill(skill)}
                aria-label={`Remove ${skill}`}
              >
                <X className="size-3" />
              </button>
            </Badge>
          ))}
        </div>
        <div className="flex items-center gap-2 mt-3">
          <Input
            id="core-skill-input"
            value={skillInput}
            onChange={(event) => setSkillInput(event.target.value)}
            placeholder="Add a skill"
            aria-labelledby="core-skill-input-label"
          />
          <Button variant="outline" size="sm" className="font-semibold" onClick={addSkill}>
            <Plus className="size-3 mr-2" />
            Add
          </Button>
        </div>
      </div>
      <div>
        <label
          htmlFor="core-cert-input"
          id="core-cert-input-label"
          className="text-xs font-semibold text-muted-foreground uppercase"
        >
          Certifications
        </label>
        <div className="flex flex-wrap gap-2 mt-2">
          {certificationsDraft.map((cert) => (
            <Badge key={cert} variant="secondary" className="flex items-center gap-1">
              {cert}
              <button
                type="button"
                className="ml-1 text-muted-foreground hover:text-foreground"
                onClick={() => removeCertification(cert)}
                aria-label={`Remove ${cert}`}
              >
                <X className="size-3" />
              </button>
            </Badge>
          ))}
        </div>
        <div className="flex items-center gap-2 mt-3">
          <Input
            id="core-cert-input"
            value={certInput}
            onChange={(event) => setCertInput(event.target.value)}
            placeholder="Add a certification"
            aria-labelledby="core-cert-input-label"
          />
          <Button variant="outline" size="sm" className="font-semibold" onClick={addCertification}>
            <Plus className="size-3 mr-2" />
            Add
          </Button>
        </div>
      </div>
    </div>
  );
}
