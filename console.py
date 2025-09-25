#!/usr/bin/python3 
import cmd
import json
import re
from models import storage
from models.base_model import BaseModel
from models.user import User
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.place import Place
from models.review import Review


class HBNBCommand(cmd.Cmd):
    prompt = "(hbnb) "
    classes = {
        "BaseModel": BaseModel,
        "User": User,
        "State": State,
        "City": City,
        "Amenity": Amenity,
        "Place": Place,
        "Review": Review,
    }
    storage = storage

    def emptyline(self):
        """Do nothing on empty input line"""
        pass

    def do_quit(self, arg):
        """Quit the program"""
        return True

    def do_EOF(self, arg):
        """Exit on EOF (Ctrl+D)"""
        return True

    # ---------- advanced (dot-notation) command handling ----------
    def default(self, line):
        match = re.fullmatch(r"(\w+)\.(\w+)\((.*)\)", line)
        if not match:
            print("*** Unknown syntax: {}".format(line))
            return
        class_name, method, args_str = match.groups()
        if class_name not in self.classes:
            print("** class doesn't exist **")
            return

        if method == "all":
            self.do_all(class_name)
            return
        if method == "count":
            cnt = len([o for o in self.storage.all().values() if o.__class__.__name__ == class_name])
            print(cnt)
            return
        if method in {"show", "destroy"}:
            arg = self._parse_id_arg(args_str)
            if arg is None:
                print("** instance id missing **")
                return
            cmd_line = f"{class_name} {arg}"
            if method == "show":
                self.do_show(cmd_line)
            else:
                self.do_destroy(cmd_line)
            return
        if method == "update":
            # two forms: ("id", "attr", value) or ("id", {dict})
            parsed = self._parse_update_args(args_str)
            if parsed is None:
                print("** instance id missing **")
                return
            obj_id, payload = parsed
            if isinstance(payload, dict):
                for k, v in payload.items():
                    self.do_update(f"{class_name} {obj_id} {k} {self._stringify(v)}")
            else:
                attr, value = payload
                self.do_update(f"{class_name} {obj_id} {attr} {self._stringify(value)}")
            return
        print("*** Unknown syntax: {}".format(line))

    def _parse_id_arg(self, args_str):
        args_str = args_str.strip()
        if not args_str:
            return None
        if args_str.startswith("\"") or args_str.startswith("'"):
            # quoted id, could contain commas/spaces
            try:
                id_match = re.match(r"^[\"']([^\"']+)[\"']\s*,?\s*$", args_str)
                if id_match:
                    return id_match.group(1)
            except Exception:
                return None
        # unquoted simple id
        parts = [p.strip() for p in args_str.split(',') if p.strip()]
        return parts[0] if parts else None

    def _parse_update_args(self, args_str):
        # returns (id, dict) or (id, (attr, value)) or None
        args_str = args_str.strip()
        if not args_str:
            return None
        # extract id first
        id_match = re.match(r"^[\"']?([^,\"']+)[\"']?\s*,\s*(.*)$", args_str)
        if not id_match:
            return None
        obj_id = id_match.group(1)
        rest = id_match.group(2).strip()
        if not rest:
            return (obj_id, None)
        # dict form
        if rest.startswith('{') and rest.endswith('}'):
            try:
                payload = json.loads(rest.replace("'", '"'))
                return (obj_id, payload)
            except Exception:
                return (obj_id, {})
        # attr, value form
        # attr may be quoted; value may be quoted
        attr_match = re.match(r"^[\"']?([^,\"']+)[\"']?\s*,\s*(.*)$", rest)
        if not attr_match:
            return (obj_id, None)
        attr = attr_match.group(1)
        value_raw = attr_match.group(2).strip()
        value = self._parse_value_token(value_raw)
        return (obj_id, (attr, value))

    def _parse_value_token(self, token):
        token = token.strip()
        if (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
            return token[1:-1]
        # try cast int/float
        try:
            if '.' in token:
                return float(token)
            return int(token)
        except ValueError:
            return token

    def _stringify(self, value):
        if isinstance(value, str):
            # escape quotes
            return '"' + value.replace('"', '\\"') + '"'
        return str(value)

    # ---------- standard commands ----------
    def do_create(self, arg):
        """Create a new instance of a class and print its id"""
        class_name = arg.strip()
        if len(class_name) == 0:
            print("** class name missing **")
        elif class_name not in HBNBCommand.classes:
            print("** class doesn't exist **")
        else:
            obj = HBNBCommand.classes[class_name]()
            obj.save()
            print(obj.id)

    def do_show(self, arg):
        """Show an instance based on the class name and id"""
        args = arg.split()
        if len(args) == 0:
            print("** class name missing **")
        elif args[0] not in HBNBCommand.classes:
            print("** class doesn't exist **")
        elif len(args) == 1:
            print("** instance id missing **")
        else:
            key = f"{args[0]}.{args[1]}"
            if key in HBNBCommand.storage.all():
                print(HBNBCommand.storage.all()[key])
            else:
                print("** no instance found **")

    def do_destroy(self, arg):
        """Delete an instance based on the class name and id"""
        args = arg.split()
        if len(args) == 0:
            print("** class name missing **")
        elif args[0] not in HBNBCommand.classes:
            print("** class doesn't exist **")
        elif len(args) == 1:
            print("** instance id missing **")
        else:
            key = f"{args[0]}.{args[1]}"
            if key in HBNBCommand.storage.all():
                del HBNBCommand.storage.all()[key]
                HBNBCommand.storage.save()
            else:
                print("** no instance found **")

    def do_all(self, arg):
        """Show all instances, or all instances of a class"""
        args = arg.split()
        if len(args) == 0:
            print([str(obj) for obj in HBNBCommand.storage.all().values()])
        elif args[0] not in HBNBCommand.classes:
            print("** class doesn't exist **")
        else:
            print([str(obj) for obj in HBNBCommand.storage.all().values()
                   if obj.__class__.__name__ == args[0]])

    def do_update(self, arg):
        """Update an instance based on the class name and id"""
        args = arg.split()
        if len(args) == 0:
            print("** class name missing **")
            return
        if args[0] not in HBNBCommand.classes:
            print("** class doesn't exist **")
            return
        if len(args) == 1:
            print("** instance id missing **")
            return

        key = f"{args[0]}.{args[1]}"
        obj_dict = HBNBCommand.storage.all()
        if key not in obj_dict:
            print("** no instance found **")
            return
        if len(args) == 2:
            print("** attribute name missing **")
            return
        if len(args) == 3:
            print("** value missing **")
            return

        obj = obj_dict[key]
        attr_name = args[2]
        attr_value = args[3]

        # cast value similarly to default handler
        if (attr_value.startswith('"') and attr_value.endswith('"')) or (attr_value.startswith("'") and attr_value.endswith("'")):
            attr_value_cast = attr_value[1:-1]
        else:
            try:
                attr_value_cast = int(attr_value)
            except ValueError:
                try:
                    attr_value_cast = float(attr_value)
                except ValueError:
                    attr_value_cast = attr_value

        if attr_name not in ["id", "created_at", "updated_at"]:
            setattr(obj, attr_name, attr_value_cast)
            obj.save()


if __name__ == "__main__":
    HBNBCommand().cmdloop()
