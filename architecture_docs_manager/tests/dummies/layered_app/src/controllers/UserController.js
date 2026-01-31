
import { UserService } from '../services/UserService';

class UserController {
    constructor() {
        this.service = new UserService();
    }
}
