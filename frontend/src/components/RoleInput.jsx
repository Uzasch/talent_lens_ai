import { useState } from 'react';
import { Check, ChevronsUpDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';

function RoleInput({ roles = [], value, onChange, onSelectExisting }) {
  const [open, setOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');

  const handleSelect = (role) => {
    onChange(role.title);
    if (onSelectExisting) {
      onSelectExisting(role);
    }
    setOpen(false);
  };

  const handleCreate = () => {
    onChange(inputValue);
    if (onSelectExisting) {
      onSelectExisting(null);
    }
    setOpen(false);
  };

  const filteredRoles = roles.filter((role) =>
    role.title.toLowerCase().includes(inputValue.toLowerCase())
  );

  const showCreateOption =
    inputValue.length > 0 &&
    !roles.some(
      (role) => role.title.toLowerCase() === inputValue.toLowerCase()
    );

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-full justify-between"
        >
          {value || "e.g., Python Developer"}
          <ChevronsUpDown className="ml-2 h-4 w-4 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[400px] p-0" align="start">
        <Command shouldFilter={false}>
          <CommandInput
            placeholder="Search or create role..."
            value={inputValue}
            onValueChange={setInputValue}
          />
          <CommandList>
            {filteredRoles.length === 0 && !showCreateOption && (
              <CommandEmpty>No roles found.</CommandEmpty>
            )}
            {showCreateOption && (
              <CommandGroup heading="Create New">
                <CommandItem onSelect={handleCreate}>
                  <span className="text-primary">+ Create</span>
                  <span className="ml-1">&quot;{inputValue}&quot;</span>
                </CommandItem>
              </CommandGroup>
            )}
            {filteredRoles.length > 0 && (
              <CommandGroup heading="Existing Roles">
                {filteredRoles.map((role) => (
                  <CommandItem
                    key={role.id}
                    value={role.title}
                    onSelect={() => handleSelect(role)}
                  >
                    <Check
                      className={cn(
                        "mr-2 h-4 w-4",
                        value === role.title ? "opacity-100" : "opacity-0"
                      )}
                    />
                    {role.title}
                    {role.candidate_count !== undefined && (
                      <span className="ml-auto text-muted-foreground text-sm">
                        {role.candidate_count} candidates
                      </span>
                    )}
                  </CommandItem>
                ))}
              </CommandGroup>
            )}
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}

export default RoleInput;
